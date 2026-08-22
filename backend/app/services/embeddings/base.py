"""
Base embedding provider interface.
"""
from abc import ABC, abstractmethod
from typing import List


class BaseEmbeddingProvider(ABC):
    """Base class for embedding providers."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    @abstractmethod
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts."""
        pass

    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """Get the embedding dimension."""
        pass

    @abstractmethod
    def estimate_cost(self, token_count: int) -> float:
        """Estimate cost in USD for token usage."""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model name."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the provider name."""
        pass
