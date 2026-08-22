"""
Embedding provider factory.
"""
from typing import Optional
from .base import BaseEmbeddingProvider
from .openai_embeddings import OpenAIEmbeddingProvider


class EmbeddingProviderFactory:
    """Factory for creating embedding provider instances."""

    @staticmethod
    def create_provider(
        provider: str,
        api_key: str,
        model: Optional[str] = None
    ) -> BaseEmbeddingProvider:
        """Create embedding provider instance."""
        provider = provider.lower()

        if provider == "openai":
            default_model = model or "text-embedding-3-small"
            return OpenAIEmbeddingProvider(api_key, default_model)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
