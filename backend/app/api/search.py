"""
Search endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.schemas import SearchResult
from app.services.search.hybrid_search import HybridSearchService
from app.services.embeddings.query_embedding import embed_query
from app.utils.rate_limit import check_rate_limit
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
    check_rate_limit(f"search:{principal.key}", settings.rate_limit_per_minute * 3, 60)
    search_service = HybridSearchService(db)

    query_embedding = await embed_query(query) if semantic else None

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
