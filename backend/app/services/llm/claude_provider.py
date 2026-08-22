"""
Claude (Anthropic) LLM provider.
"""
import anthropic
from typing import Optional
from .base import BaseLLMProvider, LLMMessage, LLMResponse


class ClaudeProvider(BaseLLMProvider):
    """Claude LLM provider using Anthropic API."""

    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        "claude-3-5-sonnet-20241022": {
            "input": 3.0,
            "output": 15.0
        },
        "claude-3-opus-20240229": {
            "input": 15.0,
            "output": 75.0
        },
        "claude-3-sonnet-20240229": {
            "input": 3.0,
            "output": 15.0
        },
        "claude-3-haiku-20240307": {
            "input": 0.25,
            "output": 1.25
        }
    }

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        super().__init__(api_key, model)
        self.client = anthropic.Anthropic(api_key=api_key)

    async def generate(
        self,
        messages: list[LLMMessage],
        max_tokens: Optional[int] = None,
        temperature: float = 0.7
    ) -> LLMResponse:
        """Generate response from Claude."""
        # Convert messages to Anthropic format
        system_message = None
        user_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                user_messages.append(
                    anthropic.messages.MessageParam(
                        role=msg.role,
                        content=msg.content
                    )
                )

        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens or 4096,
            temperature=temperature,
            system=system_message,
            messages=user_messages
        )

        # Extract token usage
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens

        # Calculate cost
        estimated_cost = self.estimate_cost(input_tokens, output_tokens)

        return LLMResponse(
            content=response.content[0].text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=self.model,
            provider=self.get_provider_name(),
            estimated_cost_usd=estimated_cost
        )

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost in USD for token usage."""
        pricing = self.PRICING.get(self.model, self.PRICING["claude-3-5-sonnet-20241022"])
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    def get_model_name(self) -> str:
        return self.model

    def get_provider_name(self) -> str:
        return "anthropic"
