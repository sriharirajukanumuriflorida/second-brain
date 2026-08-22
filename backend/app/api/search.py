"""
Search endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.schemas import SearchResult
from app.services.search.hybrid_search import HybridSearchService
from app.services.embeddings.factory import EmbeddingProviderFactory
from app.utils.auth import require_read_access, Principal
from app.utils.logger import log_search_query

router = APIRouter()


@router.get("/search", response_model=list[SearchResult])
async def search_notes(
    query: str,
    folder: str = None,
    limit: int = 20,
    semantic: bool = True,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_read_access),
):
    """Search notes.

    Runs hybrid keyword + semantic search when an embedding key is configured
    and pgvector data exists; otherwise falls back to keyword-only. Pass
    semantic=false to force keyword-only.
    """
    search_service = HybridSearchService(db)

    query_embedding = None
    if semantic and settings.embedding_api_key and settings.embedding_api_key != "your_embedding_api_key_here":
        try:
            provider = EmbeddingProviderFactory.create_provider(
                settings.embedding_provider,
                settings.embedding_api_key,
                settings.embedding_model,
            )
            embeddings = await provider.generate_embeddings([query])
            query_embedding = embeddings[0] if embeddings else None
        except Exception:
            # Embedding failure must not break search — degrade to keyword.
            query_embedding = None

    results = search_service.search(
        query=query,
        folder=folder,
        limit=limit,
        query_embedding=query_embedding,
    )

    log_search_query(db, query, len(results))

    return [
        SearchResult(
            id=r["id"],
            path=r["path"],
            title=r["title"],
            score=r["score"],
        )
        for r in results
    ]
