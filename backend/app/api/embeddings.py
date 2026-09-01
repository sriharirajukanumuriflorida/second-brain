"""
Embedding API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.embeddings.factory import EmbeddingProviderFactory
from app.services.embeddings.embedding_service import EmbeddingService
from app.services.search.hybrid_search import HybridSearchService
from app.config import settings
from app.utils.logger import log_event
from app.utils.auth import require_admin, require_read_access, Principal
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter()


def build_embedding_provider():
    """Create the embedding provider from config.

    Uses embedding_provider/embedding_model, and the dedicated embedding key
    when set, otherwise falls back to the LLM key (config allows sharing).
    Raises HTTPException(503) when no key is configured.
    """
    api_key = settings.embedding_api_key or settings.llm_api_key
    if not api_key:
        raise HTTPException(status_code=503, detail="No embedding API key configured")
    return EmbeddingProviderFactory.create_provider(
        provider=settings.embedding_provider,
        api_key=api_key,
        model=settings.embedding_model,
    )


class EmbeddingRequest(BaseModel):
    """Embedding request."""
    note_id: int = Field(..., description="Note ID to generate embeddings for")


class EmbeddingResponse(BaseModel):
    """Embedding response."""
    status: str
    chunks_created: int
    chunks_updated: int
    total_chunks: int


class ReEmbedRequest(BaseModel):
    """Re-embedding request."""
    limit: int = Field(default=100, description="Number of stale chunks to re-embed")


class ReEmbedResponse(BaseModel):
    """Re-embedding response."""
    status: str
    re_embedded: int


@router.post("/embeddings/generate", response_model=EmbeddingResponse)
async def generate_embeddings(
    request: EmbeddingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin),
):
    """Generate embeddings for a note."""
    try:
        # Create embedding provider from config
        embedding_provider = build_embedding_provider()

        # Get note
        from app.models import Note
        note = db.query(Note).filter(Note.id == request.note_id).first()
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")

        # Get note content
        from app.services.github_service import GitHubService
        github_service = GitHubService(db)
        vault_path = settings.vault_path
        note_path = vault_path / note.path

        with open(note_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Generate embeddings
        embedding_service = EmbeddingService(db, embedding_provider)
        result = await embedding_service.generate_embeddings_for_note(note, content)

        return EmbeddingResponse(
            status="completed",
            chunks_created=result["chunks_created"],
            chunks_updated=result["chunks_updated"],
            total_chunks=result["total_chunks"]
        )

    except Exception as e:
        log_event(db, "embedding.api_failed", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/embeddings/re-embed", response_model=ReEmbedResponse)
async def re_embed_stale(
    request: ReEmbedRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin),
):
    """Re-embed stale chunks."""
    try:
        # Create embedding provider from config
        embedding_provider = build_embedding_provider()

        embedding_service = EmbeddingService(db, embedding_provider)
        result = await embedding_service.re_embed_stale_chunks(request.limit)

        return ReEmbedResponse(
            status="completed",
            re_embedded=result["re_embedded"]
        )

    except Exception as e:
        log_event(db, "re-embed.failed", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


class GenerateAllRequest(BaseModel):
    """Batch embedding request."""
    only_missing: bool = Field(
        default=True,
        description="If true, only embed notes that have no chunks yet (backfill). If false, re-embed all notes."
    )
    limit: Optional[int] = Field(default=None, description="Max notes to process this call (None = all)")


class GenerateAllResponse(BaseModel):
    """Batch embedding response."""
    status: str
    notes_embedded: int
    notes_failed: int
    notes_skipped: int


@router.post("/embeddings/generate-all", response_model=GenerateAllResponse)
async def generate_all_embeddings(
    request: GenerateAllRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin),
):
    """Backfill embeddings across the vault.

    Reads note bodies from VAULT_PATH on demand. By default only processes
    notes that have no chunks yet, so it is safe to re-run. Runs inline
    (admin-triggered); for large first-time backfills the caller can page
    with ``limit``.
    """
    from app.models import Note, EmbeddingChunk

    try:
        embedding_provider = build_embedding_provider()
        embedding_service = EmbeddingService(db, embedding_provider)
        vault_path = settings.vault_path

        notes = db.query(Note).order_by(Note.id).all()

        embedded = 0
        failed = 0
        skipped = 0

        for note in notes:
            if request.limit is not None and embedded >= request.limit:
                break

            if request.only_missing:
                has_chunks = db.query(EmbeddingChunk).filter(
                    EmbeddingChunk.note_id == note.id
                ).first() is not None
                if has_chunks:
                    skipped += 1
                    continue

            note_path = vault_path / note.path
            try:
                with open(note_path, "r", encoding="utf-8") as f:
                    content = f.read()
                await embedding_service.generate_embeddings_for_note(note, content)
                embedded += 1
            except Exception as e:
                log_event(db, "embedding.batch_note_failed", {"path": note.path, "error": str(e)})
                failed += 1
                continue

        return GenerateAllResponse(
            status="completed",
            notes_embedded=embedded,
            notes_failed=failed,
            notes_skipped=skipped,
        )

    except HTTPException:
        raise
    except Exception as e:
        log_event(db, "embedding.batch_failed", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/embeddings/status")
async def get_embedding_status(
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_read_access),
):
    """Get embedding status."""
    from app.models import EmbeddingChunk

    total_chunks = db.query(EmbeddingChunk).count()
    stale_chunks = db.query(EmbeddingChunk).filter(EmbeddingChunk.is_stale == True).count()

    return {
        "total_chunks": total_chunks,
        "stale_chunks": stale_chunks,
        "semantic_search_available": total_chunks > 0
    }
