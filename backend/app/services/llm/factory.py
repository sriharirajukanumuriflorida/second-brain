"""
LLM provider factory.
"""
from typing import Optional
from .base import BaseLLMProvider
from .claude_provider import ClaudeProvider
from .openai_provider import OpenAIProvider


class LLMProviderFactory:
    """Factory for creating LLM provider instances."""

    @staticmethod
    def create_provider(
        provider: str,
        api_key: str,
        model: Optional[str] = None,
        base_url: Optional[str] = None
    ) -> BaseLLMProvider:
        """Create LLM provider instance."""
        provider = provider.lower()

        if provider == "anthropic" or provider == "claude":
            default_model = model or "claude-3-5-sonnet-20241022"
            return ClaudeProvider(api_key, default_model)
        elif provider == "openai":
            default_model = model or "gpt-4o"
            return OpenAIProvider(api_key, default_model, base_url)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
