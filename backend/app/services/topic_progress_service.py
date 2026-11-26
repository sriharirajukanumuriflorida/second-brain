"""
Shared TopicProgress read/write logic — used by both the dashboard-driven
/progress/topic route and the in-chat completion-signal flow (chat_quiz_flow.py),
so there is exactly one place that writes a topic's status.
"""
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.models import TopicProgress


def mark_topic_status(db: Session, user_id: int, note_path: str, status: str) -> TopicProgress:
    row = (
        db.query(TopicProgress)
        .filter(TopicProgress.user_id == user_id, TopicProgress.note_path == note_path)
        .first()
    )
    if row is None:
        row = TopicProgress(user_id=user_id, note_path=note_path, status=status)
        db.add(row)
    else:
        row.status = status

    if status == "done":
        row.completed_at = func.now()

    db.commit()
    db.refresh(row)
    return row
