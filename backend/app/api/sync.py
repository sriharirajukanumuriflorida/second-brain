"""
Sync endpoints.
"""
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import SyncRequest, SyncResponse
from app.services.github_service import GitHubService
from app.services.index_service import IndexService
from app.services.embeddings.factory import EmbeddingProviderFactory
from app.services.embeddings.embedding_service import EmbeddingService
from app.models import SyncEvent, Note
from app.config import settings
from app.utils.logger import log_sync_started, log_sync_completed, log_sync_failed, log_event
from app.utils.auth import require_admin
from pathlib import Path
from datetime import datetime

router = APIRouter()


@router.post("/sync", response_model=SyncResponse)
async def trigger_sync(
    request: SyncRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin),
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

        # Generate embeddings for notes that changed this run. Runs after
        # index_vault() commits so new notes have DB ids. Best-effort: an
        # embedding failure must not fail the sync itself.
        embedded = await embed_changed_notes(
            db, Path(vault_path), stats.get("changed_paths", [])
        )

        # Update sync event
        sync_event.status = "completed"
        sync_event.completed_at = datetime.utcnow()
        sync_event.notes_processed = stats["processed"]
        sync_event.notes_indexed = stats["indexed"]
        sync_event.notes_updated = stats["updated"]
        db.commit()

        log_sync_completed(db, sync_id, stats["processed"])
        log_event(db, "sync.embeddings_generated", {
            "sync_id": sync_id,
            "notes_embedded": embedded,
            "notes_changed": len(stats.get("changed_paths", [])),
        })

    except Exception as e:
        sync_event.status = "failed"
        sync_event.completed_at = datetime.utcnow()
        sync_event.error_message = str(e)
        db.commit()

        log_sync_failed(db, sync_id, str(e))


def _build_embedding_provider():
    """Create the embedding provider from config.

    Falls back to the LLM API key when a dedicated embedding key is not set
    (config allows them to be the same). Returns None when no key is
    available so keyword-only deployments skip embedding without erroring.
    """
    api_key = settings.embedding_api_key or settings.llm_api_key
    if not api_key:
        return None
    return EmbeddingProviderFactory.create_provider(
        provider=settings.embedding_provider,
        api_key=api_key,
        model=settings.embedding_model,
    )


async def embed_changed_notes(db: Session, vault_path: Path, changed_paths: list) -> int:
    """Generate embeddings for the notes whose content changed this sync.

    Best-effort per note: a failure on one note is logged and skipped so the
    sync still completes. Returns the count of notes successfully embedded.
    """
    if not changed_paths:
        return 0

    provider = _build_embedding_provider()
    if provider is None:
        log_event(db, "sync.embeddings_skipped", {"reason": "no_embedding_api_key"})
        return 0

    embedding_service = EmbeddingService(db, provider)
    embedded = 0

    for relative_path in changed_paths:
        note = db.query(Note).filter(Note.path == relative_path).first()
        if note is None:
            continue
        note_file = vault_path / note.path
        try:
            with open(note_file, "r", encoding="utf-8") as f:
                content = f.read()
            await embedding_service.generate_embeddings_for_note(note, content)
            embedded += 1
        except Exception as e:
            log_event(db, "sync.embed_note_failed", {"path": relative_path, "error": str(e)})
            continue

    return embedded
