"""
Topic progress endpoints — per-user completion tracking.

Writes require a real logged-in user (get_current_user), not just read
access, so a shared read-only link visitor can't write progress on someone
else's account.
"""
from collections import defaultdict
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import QuizAttempt, TopicProgress, User
from app.schemas import (
    PhaseProgress,
    ProgressSummaryResponse,
    TopicProgressEntry,
    TopicStatusUpdate,
)
from app.services.topic_progress_service import mark_topic_status
from app.services.topic_registry import TOPICS
from app.utils.auth import get_current_user

router = APIRouter()


def build_progress_summary(db: Session, user_id: int) -> ProgressSummaryResponse:
    progress_rows = {
        p.note_path: p
        for p in db.query(TopicProgress).filter(TopicProgress.user_id == user_id).all()
    }

    attempts_by_path: Dict[str, List[QuizAttempt]] = defaultdict(list)
    for attempt in db.query(QuizAttempt).filter(QuizAttempt.user_id == user_id).all():
        attempts_by_path[attempt.note_path].append(attempt)

    phases: Dict[str, List[TopicProgressEntry]] = defaultdict(list)
    all_entries: List[TopicProgressEntry] = []

    for topic in TOPICS:
        note_path = topic["note_path"]
        progress = progress_rows.get(note_path)
        attempts = attempts_by_path.get(note_path, [])
        average_score: Optional[float] = (
            sum(a.score for a in attempts) / len(attempts) if attempts else None
        )
        entry = TopicProgressEntry(
            note_path=note_path,
            label=topic["label"],
            status=progress.status if progress else "not_started",
            completed_at=progress.completed_at if progress else None,
            attempt_count=len(attempts),
            average_score=average_score,
            last_score=attempts[-1].score if attempts else None,
        )
        phases[topic["phase"]].append(entry)
        all_entries.append(entry)

    phase_list = [
        PhaseProgress(
            phase=phase_name,
            total_topics=len(entries),
            done_topics=sum(1 for e in entries if e.status == "done"),
            topics=entries,
        )
        for phase_name, entries in phases.items()
    ]

    weak_topics = sorted(
        (e for e in all_entries if e.average_score is None or e.average_score < 70),
        key=lambda e: (e.average_score is not None, e.average_score or 0),
    )[:10]

    return ProgressSummaryResponse(
        phases=phase_list,
        total_topics=len(all_entries),
        done_topics=sum(1 for e in all_entries if e.status == "done"),
        weak_topics=weak_topics,
    )


@router.get("/progress/summary", response_model=ProgressSummaryResponse)
async def get_progress_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Per-phase completion + quiz performance summary for the Progress page."""
    return build_progress_summary(db, current_user.id)


@router.post("/progress/topic")
async def set_topic_status(
    request: TopicStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a topic's completion status."""
    row = mark_topic_status(db, current_user.id, request.note_path, request.status)
    return {"note_path": row.note_path, "status": row.status}
