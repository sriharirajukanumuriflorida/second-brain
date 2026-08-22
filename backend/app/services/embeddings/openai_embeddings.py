"""
OpenAI embedding provider.
"""
from openai import AsyncOpenAI
from typing import List
from .base import BaseEmbeddingProvider


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """OpenAI embedding provider."""

    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        "text-embedding-3-small": 0.02,
        "text-embedding-3-large": 0.13,
        "text-embedding-ada-002": 0.10
    }

    # Embedding dimensions
    DIMENSIONS = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536
    }

    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        super().__init__(api_key, model)
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts."""
        response = await self.client.embeddings.create(
            model=self.model,
            input=texts
        )

        return [item.embedding for item in response.data]

    def get_embedding_dimension(self) -> int:
        """Get the embedding dimension."""
        return self.DIMENSIONS.get(self.model, 1536)

    def estimate_cost(self, token_count: int) -> float:
        """Estimate cost in USD for token usage."""
        pricing = self.PRICING.get(self.model, self.PRICING["text-embedding-3-small"])
        return (token_count / 1_000_000) * pricing

    def get_model_name(self) -> str:
        return self.model

    def get_provider_name(self) -> str:
        return "openai"
