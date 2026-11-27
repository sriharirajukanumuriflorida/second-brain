"""
Quiz endpoints — the dashboard-driven drill flow.

This is the "front door" alternative to the in-chat quiz flow in
mentor_chat_workflow.py; both call the same underlying services
(qa_parser_service, QuizScoringWorkflow) rather than duplicating logic.
"""
import random
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import QuizAttempt, User
from app.schemas import (
    QuizQuestionResponse,
    QuizResultResponse,
    QuizSubmitRequest,
    QuizTopicsResponse,
)
from app.services.llm.factory import LLMProviderFactory
from app.utils.rate_limit import check_rate_limit
from app.services.workflows.quiz_scoring_workflow import JudgeScoringError
from app.services.qa_parser_service import extract_qa_pairs
from app.services.topic_registry import TOPICS, find_by_note_path
from app.services.workflows.factory import WorkflowFactory
from app.utils.auth import get_current_user

router = APIRouter()


def read_note_qa_pairs(note_path: str):
    """Read a note's raw content off disk and extract its Q&A pairs.

    Returns [] if the note file can't be read or has no Interview Q&A
    section — this is a best-effort lookup, not a hard failure, mirroring
    hybrid_search.py's existing OSError-tolerant file-read pattern.
    """
    note_file = settings.vault_path_resolved / note_path
    try:
        with open(note_file, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError:
        return []
    return extract_qa_pairs(content)


@router.get("/quiz/topics", response_model=QuizTopicsResponse)
async def list_quiz_topics(
    current_user: User = Depends(get_current_user),
):
    """List quizzable topics (note_path + label) for picking what to drill."""
    return QuizTopicsResponse(topics=[{"note_path": t["note_path"], "label": t["label"]} for t in TOPICS])


@router.get("/quiz/question", response_model=QuizQuestionResponse)
async def get_quiz_question(
    note_path: str = Query(...),
    current_user: User = Depends(get_current_user),
):
    """Return one random question from a note's Interview Q&A section."""
    topic = find_by_note_path(note_path)
    if topic is None:
        raise HTTPException(status_code=404, detail="Unknown topic note_path")

    pairs = read_note_qa_pairs(note_path)
    if not pairs:
        raise HTTPException(status_code=404, detail="This topic has no Interview Q&A section to quiz from")

    chosen = random.choice(pairs)
    return QuizQuestionResponse(note_path=note_path, question=chosen["question"])


@router.post("/quiz/submit", response_model=QuizResultResponse)
async def submit_quiz_answer(
    request: QuizSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Score a quiz answer via the LLM judge and persist the attempt."""
    check_rate_limit(f"quiz:user:{current_user.id}", settings.rate_limit_per_minute, 60)
    pairs = read_note_qa_pairs(request.note_path)
    matching = next((p for p in pairs if p["question"] == request.question), None)
    if matching is None:
        raise HTTPException(status_code=404, detail="Question not found for this topic — it may be stale")

    llm_provider = LLMProviderFactory.create_provider(
        provider=settings.llm_provider,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
    )
    workflow = WorkflowFactory.create_workflow("quiz-scoring", db, llm_provider)
    try:
        result = await workflow.execute({
            "question": matching["question"],
            "reference_answer": matching["reference_answer"],
            "one_liner": matching["one_liner"],
            "user_answer": request.user_answer,
            "hints_given": request.hints_given,
        })
    except JudgeScoringError:
        raise HTTPException(status_code=502, detail="Could not score this answer automatically. Please try again.")

    attempt = QuizAttempt(
        user_id=current_user.id,
        note_path=request.note_path,
        question=matching["question"],
        reference_answer=matching["reference_answer"],
        user_answer=request.user_answer,
        score=result["score"],
        feedback=result["feedback"],
        hints_given=len(request.hints_given),
        model=result["model"],
        input_tokens=result["input_tokens"],
        output_tokens=result["output_tokens"],
    )
    db.add(attempt)
    db.commit()

    return QuizResultResponse(
        score=result["score"],
        feedback=result["feedback"],
        reference_answer=matching["reference_answer"],
        hints_given=len(request.hints_given),
        reinforcement=result["reinforcement"],
    )
