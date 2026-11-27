"""Embed a search query with the server's embedding key. Returns None when
unconfigured or on any failure so callers degrade to keyword search."""
from typing import List, Optional

from app.config import settings
from app.services.embeddings.factory import EmbeddingProviderFactory


async def embed_query(query: str) -> Optional[List[float]]:
    if not settings.embedding_api_key or settings.embedding_api_key == "your_embedding_api_key_here":
        return None
    try:
        provider = EmbeddingProviderFactory.create_provider(
            settings.embedding_provider,
            settings.embedding_api_key,
            settings.embedding_model,
        )
        embeddings = await provider.generate_embeddings([query])
        return embeddings[0] if embeddings else None
    except Exception:
        return None
