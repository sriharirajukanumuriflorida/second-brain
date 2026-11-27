"""
In-chat quiz flow: completion-signal detection, the yes/no test offer, and the
question -> (clarification | hint | answer) -> score loop, all living inside
one ChatSession's pending_quiz_state field.

Called from chat.py BEFORE the normal MentorChatWorkflow RAG path runs. If
this module handles the turn (returns a non-None result), chat.py should
return that reply directly and skip the normal workflow call for this turn.

Requires a real logged-in user (user_id is not None) — a shared read-only
link visitor has no account to write TopicProgress/QuizAttempt against, so
the whole flow is a no-op for them (handled by the caller checking user_id
before calling into this module at all).
"""
import json
import random
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.config import settings
from app.models import ChatSession, QuizAttempt
from app.services.topic_progress_service import mark_topic_status
from app.services.llm.base import LLMMessage
from app.services.llm.factory import LLMProviderFactory
from app.services.prompts.quiz_judge import (
    CLASSIFY_SYSTEM_PROMPT,
    CLASSIFY_USER_TEMPLATE,
    HINT_SYSTEM_PROMPT,
    REPHRASE_SYSTEM_PROMPT,
)
from app.services.qa_parser_service import extract_qa_pairs
from app.services.topic_registry import find_by_label_fragment
from app.services.workflows.factory import WorkflowFactory
from app.services.workflows.quiz_scoring_workflow import JudgeScoringError
from app.utils.logger import log_event

MAX_ASSISTS_PER_QUESTION = 2


def _read_qa_pairs(note_path: str):
    note_file = settings.vault_path_resolved / note_path
    try:
        with open(note_file, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError:
        return []
    return extract_qa_pairs(content)


def _get_pending_state(session: ChatSession) -> Optional[dict]:
    if not session.pending_quiz_state:
        return None
    try:
        return json.loads(session.pending_quiz_state)
    except (TypeError, ValueError):
        return None


def _set_pending_state(db: Session, session: ChatSession, state: Optional[dict]) -> None:
    session.pending_quiz_state = json.dumps(state) if state else None
    db.commit()


def _make_llm_provider():
    return LLMProviderFactory.create_provider(
        provider=settings.llm_provider,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
    )


class _UsageAccumulator:
    """Tracks token/cost usage across however many LLM calls one turn makes
    (classify + rephrase, classify + hint, or classify + score), so the reply
    sent back to the user reflects real usage instead of silently dropping it."""

    def __init__(self):
        self.input_tokens = 0
        self.output_tokens = 0
        self.estimated_cost_usd = 0.0
        self.model: Optional[str] = None
        self.provider: Optional[str] = None

    def add(self, response) -> None:
        self.input_tokens += response.input_tokens
        self.output_tokens += response.output_tokens
        self.estimated_cost_usd += response.estimated_cost_usd
        self.model = response.model
        self.provider = response.provider


async def _classify_message(llm_provider, question: str, message: str, usage: _UsageAccumulator) -> str:
    """Returns "clarification_request" | "hint_request" | "attempted_answer"."""
    import re

    messages = [
        LLMMessage(role="system", content=CLASSIFY_SYSTEM_PROMPT.format(question=question)),
        LLMMessage(role="user", content=CLASSIFY_USER_TEMPLATE.format(message=message)),
    ]
    response = await llm_provider.generate(messages, max_tokens=100, temperature=0.0)
    usage.add(response)
    match = re.search(r"\{.*\}", response.content, re.DOTALL)
    if not match:
        return "attempted_answer"  # fail safe: treat unparseable classification as an answer attempt
    try:
        parsed = json.loads(match.group(0))
        classification = parsed.get("classification")
        if classification in {"clarification_request", "hint_request", "attempted_answer"}:
            return classification
    except (ValueError, KeyError):
        pass
    return "attempted_answer"


async def handle_turn(
    db: Session,
    session: ChatSession,
    user_id: int,
    message: str,
) -> Optional[Dict[str, Any]]:
    """Returns a chat-response-shaped dict if this module handled the turn
    (completion signal, pending offer/question/clarification/hint/answer),
    or None if the message should fall through to the normal RAG workflow.
    """
    pending = _get_pending_state(session)

    if pending is None:
        return _try_detect_completion(db, session, user_id, message)

    if pending["stage"] == "awaiting_consent":
        return await _handle_consent_stage(db, session, pending, message)

    if pending["stage"] == "awaiting_answer":
        return await _handle_answer_stage(db, session, user_id, pending, message)

    # Unknown stage — clear and fall through rather than get stuck.
    _set_pending_state(db, session, None)
    return None


def _try_detect_completion(
    db: Session, session: ChatSession, user_id: int, message: str
) -> Optional[Dict[str, Any]]:
    topic = find_by_label_fragment(message)
    if topic is None:
        return None

    completion_phrases = ["done", "finished", "completed", "mark", "i get it", "i understand"]
    if not any(p in message.lower() for p in completion_phrases):
        return None

    mark_topic_status(db, user_id, topic["note_path"], "done")
    _set_pending_state(db, session, {
        "note_path": topic["note_path"],
        "stage": "awaiting_consent",
    })

    reply = (
        f"Nice — marked **{topic['label']}** as done. "
        f"Want to test yourself on it with a couple of interview-style questions? (yes/no)"
    )
    return _reply(reply)


async def _handle_consent_stage(
    db: Session, session: ChatSession, pending: dict, message: str
) -> Dict[str, Any]:
    lowered = message.strip().lower()
    if lowered in {"yes", "y", "yeah", "yep", "sure", "ok", "okay"}:
        pairs = _read_qa_pairs(pending["note_path"])
        if not pairs:
            _set_pending_state(db, session, None)
            return _reply("This topic doesn't have any interview questions written up yet — nothing to quiz you on.")

        chosen = random.choice(pairs)
        _set_pending_state(db, session, {
            **pending,
            "stage": "awaiting_answer",
            "question": chosen["question"],
            "reference_answer": chosen["reference_answer"],
            "one_liner": chosen["one_liner"],
            "assist_count": 0,
            "hints_given": [],
        })
        return _reply(chosen["question"])

    # Anything else: decline, clear state, fall through to normal RAG for this same message.
    _set_pending_state(db, session, None)
    return None


async def _handle_answer_stage(
    db: Session, session: ChatSession, user_id: int, pending: dict, message: str
) -> Dict[str, Any]:
    llm_provider = _make_llm_provider()
    usage = _UsageAccumulator()
    classification = await _classify_message(llm_provider, pending["question"], message, usage)

    if classification in {"clarification_request", "hint_request"}:
        if pending["assist_count"] >= MAX_ASSISTS_PER_QUESTION:
            _set_pending_state(db, session, None)
            return _reply(
                "Let's leave it there for this one — want to move on, or try answering with what you've got?",
                usage=usage,
            )

        if classification == "clarification_request":
            messages = [LLMMessage(
                role="system",
                content=REPHRASE_SYSTEM_PROMPT.format(question=pending["question"]),
            )]
            response = await llm_provider.generate(messages, max_tokens=200, temperature=0.3)
            usage.add(response)
            reply_text = response.content.strip()
        else:  # hint_request
            messages = [LLMMessage(
                role="system",
                content=HINT_SYSTEM_PROMPT.format(
                    question=pending["question"],
                    reference_answer=pending["reference_answer"],
                ),
            )]
            response = await llm_provider.generate(messages, max_tokens=150, temperature=0.4)
            usage.add(response)
            reply_text = response.content.strip()
            pending["hints_given"].append(reply_text)

        pending["assist_count"] += 1
        _set_pending_state(db, session, pending)
        return _reply(reply_text, usage=usage)

    # attempted_answer
    workflow = WorkflowFactory.create_workflow("quiz-scoring", db, llm_provider)
    try:
        result = await workflow.execute({
            "question": pending["question"],
            "reference_answer": pending["reference_answer"],
            "one_liner": pending.get("one_liner"),
            "user_answer": message,
            "hints_given": pending.get("hints_given", []),
        })
    except JudgeScoringError:
        # Keep the pending question so the user can resend; record nothing.
        return _reply("I couldn't score that answer just now. Please send it again.", usage=usage)
    usage.input_tokens += result["input_tokens"]
    usage.output_tokens += result["output_tokens"]
    usage.estimated_cost_usd += result["estimated_cost_usd"]
    usage.model = result["model"]
    usage.provider = result["provider"]

    db.add(QuizAttempt(
        user_id=user_id,
        note_path=pending["note_path"],
        question=pending["question"],
        reference_answer=pending["reference_answer"],
        user_answer=message,
        score=result["score"],
        feedback=result["feedback"],
        hints_given=len(pending.get("hints_given", [])),
        model=result["model"],
        input_tokens=result["input_tokens"],
        output_tokens=result["output_tokens"],
    ))
    _set_pending_state(db, session, None)
    db.commit()

    log_event(db, "chat_quiz.scored", {"note_path": pending["note_path"], "score": result["score"]})

    reply_lines = [f"Score: {result['score']}/100 — {result['feedback']}"]
    if result.get("reinforcement"):
        reply_lines.append(f"\nHere's the mental model worth remembering: {result['reinforcement']}")
    return _reply("\n".join(reply_lines), usage=usage)


def _reply(text: str, usage: Optional[_UsageAccumulator] = None) -> Dict[str, Any]:
    """Builds a chat-response-shaped dict matching MentorChatWorkflow's return
    shape. Pass `usage` for replies that made one or more real LLM calls (so
    token/cost accounting isn't silently dropped) — omit it for purely
    scripted, deterministic replies (e.g. the completion-offer message) that
    made no LLM call at all."""
    return {
        "reply": text,
        "source_notes": [],
        "web_sources": [],
        "model": usage.model if usage else None,
        "provider": usage.provider if usage else None,
        "input_tokens": usage.input_tokens if usage else 0,
        "output_tokens": usage.output_tokens if usage else 0,
        "estimated_cost_usd": usage.estimated_cost_usd if usage else 0.0,
        "cached": False,
    }
