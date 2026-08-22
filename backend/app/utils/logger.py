"""
Audit logging utility.
"""
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict
from sqlalchemy.orm import Session
from app.models import AuditLog

# Configure structured JSON logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def log_event(
    db: Session,
    event_type: str,
    event_data: Dict[str, Any]
) -> AuditLog:
    """Log an audit event to database."""
    audit_log = AuditLog(
        event_type=event_type,
        event_data=json.dumps(event_data)
    )
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)

    # Also log to console
    log_entry = {
        "event": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **event_data
    }
    logger.info(json.dumps(log_entry))

    return audit_log


def log_sync_started(db: Session, sync_id: int) -> None:
    """Log sync started event."""
    log_event(db, "sync.started", {"sync_id": sync_id})


def log_sync_completed(db: Session, sync_id: int, notes_processed: int) -> None:
    """Log sync completed event."""
    log_event(
        db,
        "sync.completed",
        {"sync_id": sync_id, "notes_processed": notes_processed}
    )


def log_sync_failed(db: Session, sync_id: int, error: str) -> None:
    """Log sync failed event."""
    log_event(db, "sync.failed", {"sync_id": sync_id, "error": error})


def log_search_query(db: Session, query: str, results_count: int) -> None:
    """Log search query event."""
    log_event(
        db,
        "search.query",
        {"query": query, "results_count": results_count}
    )
