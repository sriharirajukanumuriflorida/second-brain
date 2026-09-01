"""
Status endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import StatusResponse
from app.models import Note, SyncEvent
from app.config import settings
from sqlalchemy import desc, or_
from app.utils.auth import require_read_access, Principal

router = APIRouter()


@router.get("/status", response_model=StatusResponse)
async def get_status(
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_read_access),
):
    """Get vault sync and index status."""
    total_notes = db.query(Note).filter(
        Note.is_archived == False,
        or_(*[Note.folder.like(f"{digit}%") for digit in "0123456789"]),
        Note.folder != "14 Agent Outputs",
    ).count()

    # Get last sync event
    last_sync = db.query(SyncEvent).order_by(desc(SyncEvent.started_at)).first()

    return StatusResponse(
        total_notes=total_notes,
        last_sync_at=last_sync.started_at if last_sync else None,
        last_sync_status=last_sync.status if last_sync else None,
        vault_path=str(settings.vault_path_resolved)
    )
