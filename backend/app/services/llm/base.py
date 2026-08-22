"""
Base LLM provider interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel


class LLMMessage(BaseModel):
    """Message for LLM conversation."""
    role: str  # "user", "assistant", "system"
    content: str


class LLMResponse(BaseModel):
    """Response from LLM provider."""
    content: str
    input_tokens: int
    output_tokens: int
    model: str
    provider: str
    estimated_cost_usd: float


class BaseLLMProvider(ABC):
    """Base class for LLM providers."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    @abstractmethod
    async def generate(
        self,
        messages: list[LLMMessage],
        max_tokens: Optional[int] = None,
        temperature: float = 0.7
    ) -> LLMResponse:
        """Generate response from LLM."""
        pass

    @abstractmethod
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
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
