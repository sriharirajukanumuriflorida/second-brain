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
        # Create embedding provider
        embedding_provider = EmbeddingProviderFactory.create_provider(
            provider="openai",
            api_key=settings.llm_api_key,
            model="text-embedding-3-small"
        )

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
        # Create embedding provider
        embedding_provider = EmbeddingProviderFactory.create_provider(
            provider="openai",
            api_key=settings.llm_api_key,
            model="text-embedding-3-small"
        )

        embedding_service = EmbeddingService(db, embedding_provider)
        result = await embedding_service.re_embed_stale_chunks(request.limit)

        return ReEmbedResponse(
            status="completed",
            re_embedded=result["re_embedded"]
        )

    except Exception as e:
        log_event(db, "re-embed.failed", {"error": str(e)})
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
