"""
Sync endpoints.
"""
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import SyncRequest, SyncResponse
from app.services.github_service import GitHubService
from app.services.index_service import IndexService
from app.models import SyncEvent
from app.config import settings
from app.utils.logger import log_sync_started, log_sync_completed, log_sync_failed
from pathlib import Path
from datetime import datetime

router = APIRouter()


@router.post("/sync", response_model=SyncResponse)
async def trigger_sync(
    request: SyncRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Trigger vault sync and indexing."""
    # Create sync event
    sync_event = SyncEvent(status="started")
    db.add(sync_event)
    db.commit()
    db.refresh(sync_event)

    # Log sync started
    log_sync_started(db, sync_event.id)

    # Run sync in background
    background_tasks.add_task(
        run_sync_task,
        db,
        sync_event.id,
        request.force
    )

    return SyncResponse(
        sync_id=sync_event.id,
        status="started",
        message="Sync started in background"
    )


async def run_sync_task(db: Session, sync_id: int, force: bool):
    """Background task for sync and indexing."""
    sync_event = db.query(SyncEvent).filter(SyncEvent.id == sync_id).first()

    try:
        # Clone/fetch repository
        github_service = GitHubService(db)
        vault_path = github_service.clone_or_fetch_repo(force=force)

        # Pull latest
        github_service.pull_latest()

        # Index vault
        index_service = IndexService(db, Path(vault_path))
        stats = index_service.index_vault()

        # Update sync event
        sync_event.status = "completed"
        sync_event.completed_at = datetime.utcnow()
        sync_event.notes_processed = stats["processed"]
        sync_event.notes_indexed = stats["indexed"]
        sync_event.notes_updated = stats["updated"]
        db.commit()

        log_sync_completed(db, sync_id, stats["processed"])

    except Exception as e:
        sync_event.status = "failed"
        sync_event.completed_at = datetime.now(timezone.utc)
        sync_event.error_message = str(e)
        db.commit()

        log_sync_failed(db, sync_id, str(e))
