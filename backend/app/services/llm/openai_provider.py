"""
OpenAI/Azure OpenAI LLM provider.
"""
from openai import AsyncOpenAI
from typing import Optional
from .base import BaseLLMProvider, LLMMessage, LLMResponse


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider using OpenAI API."""

    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        "gpt-4o": {
            "input": 5.0,
            "output": 15.0
        },
        "gpt-4-turbo": {
            "input": 10.0,
            "output": 30.0
        },
        "gpt-3.5-turbo": {
            "input": 0.5,
            "output": 1.5
        }
    }

    def __init__(self, api_key: str, model: str = "gpt-4o", base_url: Optional[str] = None):
        super().__init__(api_key, model)
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def generate(
        self,
        messages: list[LLMMessage],
        max_tokens: Optional[int] = None,
        temperature: float = 0.7
    ) -> LLMResponse:
        """Generate response from OpenAI."""
        # Convert messages to OpenAI format
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # Call OpenAI API
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            max_tokens=max_tokens or 4096,
            temperature=temperature
        )

        # Extract token usage
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

        # Calculate cost
        estimated_cost = self.estimate_cost(input_tokens, output_tokens)

        return LLMResponse(
            content=response.choices[0].message.content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=self.model,
            provider=self.get_provider_name(),
            estimated_cost_usd=estimated_cost
        )

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost in USD for token usage."""
        pricing = self.PRICING.get(self.model, self.PRICING["gpt-4o"])
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    def get_model_name(self) -> str:
        return self.model

    def get_provider_name(self) -> str:
        return "openai"
