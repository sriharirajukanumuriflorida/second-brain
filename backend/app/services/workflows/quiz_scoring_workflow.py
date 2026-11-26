"""
Quiz answer scoring workflow — LLM-as-judge.

Scores a user's answer against a note's own reference answer (semantic match,
not literal/keyword match), factoring in any hints the user was given before
answering, and surfaces the note's own "one-liner" as a durable mental-model
reinforcement when the score is weak.
"""
import json
import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ValidationError

from app.services.workflows.base import BaseWorkflow
from app.services.llm.base import LLMMessage
from app.services.prompts.quiz_judge import (
    QUIZ_JUDGE_SYSTEM_PROMPT,
    QUIZ_JUDGE_USER_TEMPLATE,
)
from app.utils.logger import log_event

REINFORCEMENT_THRESHOLD = 70


class _JudgeResult(BaseModel):
    score: int
    feedback: str


def _extract_json(text: str) -> dict:
    """Best-effort extraction of a JSON object from an LLM response that may
    include stray prose/markdown fences around the JSON."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("no JSON object found in response")
    return json.loads(match.group(0))


class QuizScoringWorkflow(BaseWorkflow):
    """LLM-as-judge scoring for a single quiz answer."""

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        question: str = context["question"]
        reference_answer: str = context["reference_answer"]
        user_answer: str = context["user_answer"]
        one_liner: Optional[str] = context.get("one_liner")
        hints_given: List[str] = context.get("hints_given", [])

        hints_block = (
            "\n".join(f"- {h}" for h in hints_given) if hints_given else "(none)"
        )

        system_prompt = QUIZ_JUDGE_SYSTEM_PROMPT.format(
            question=question,
            reference_answer=reference_answer,
            hints_given=hints_block,
        )
        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(
                role="user",
                content=QUIZ_JUDGE_USER_TEMPLATE.format(user_answer=user_answer),
            ),
        ]

        result = await self._judge_with_retry(messages)

        log_event(self.db, "workflow.completed", {
            "workflow": self.get_workflow_name(),
            "score": result.score,
            "input_tokens": result.input_tokens,
            "output_tokens": result.output_tokens,
            "cost_usd": result.estimated_cost_usd,
            "model": result.model,
        })

        reinforcement = (
            one_liner if result.score < REINFORCEMENT_THRESHOLD and one_liner else None
        )

        return {
            "score": result.score,
            "feedback": result.feedback,
            "reinforcement": reinforcement,
            "below_threshold": result.score < REINFORCEMENT_THRESHOLD,
            "hints_given": len(hints_given),
            "model": result.model,
            "provider": result.provider,
            "input_tokens": result.input_tokens,
            "output_tokens": result.output_tokens,
            "estimated_cost_usd": result.estimated_cost_usd,
        }

    async def _judge_with_retry(self, messages: List[LLMMessage]):
        """Call the judge LLM, validate the structured output, and retry once
        on malformed JSON before giving up — mirrors this vault's own
        "validate before trusting, bounded retries" principle for structured
        LLM output rather than crashing or silently accepting garbage."""
        last_error: Optional[Exception] = None
        response = None
        for _ in range(2):
            response = await self.llm_provider.generate(messages, max_tokens=512, temperature=0.2)
            try:
                parsed = _JudgeResult(**_extract_json(response.content))
                return _ScoredResponse(parsed, response)
            except (ValueError, ValidationError) as exc:
                last_error = exc
                continue

        log_event(self.db, "quiz_judge.malformed_output", {"error": str(last_error)})
        # Fail safe rather than raise: a malformed judge response shouldn't crash
        # the chat turn or the quiz route — surface a neutral, clearly-flagged
        # result instead so the caller can decide how to handle it.
        return _ScoredResponse(
            _JudgeResult(score=0, feedback="Could not score this answer automatically — please try again."),
            response,
        )

    def get_workflow_name(self) -> str:
        return "quiz-scoring"


class _ScoredResponse:
    """Bundles the validated judge output with the underlying LLM response's
    token/cost metadata, so callers get one object instead of two."""

    def __init__(self, judge_result: _JudgeResult, llm_response):
        self.score = judge_result.score
        self.feedback = judge_result.feedback
        self.model = llm_response.model if llm_response else None
        self.provider = llm_response.provider if llm_response else None
        self.input_tokens = llm_response.input_tokens if llm_response else 0
        self.output_tokens = llm_response.output_tokens if llm_response else 0
        self.estimated_cost_usd = llm_response.estimated_cost_usd if llm_response else 0.0
