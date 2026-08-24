"""
Claude (Anthropic) LLM provider.
"""
import anthropic
from typing import Optional, List
from .base import BaseLLMProvider, LLMMessage, LLMResponse


class ClaudeProvider(BaseLLMProvider):
    """Claude LLM provider using Anthropic API."""

    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        "claude-haiku-4-5":            {"input": 0.80, "output": 4.0},
        "claude-sonnet-4-5":           {"input": 3.0,  "output": 15.0},
        "claude-3-5-sonnet-20241022":  {"input": 3.0,  "output": 15.0},
        "claude-3-5-haiku-20241022":   {"input": 0.80, "output": 4.0},
        "claude-3-opus-20240229":      {"input": 15.0, "output": 75.0},
        "claude-3-haiku-20240307":     {"input": 0.25, "output": 1.25},
    }

    # Native web search tool definition (Claude 3.5+ Sonnet)
    WEB_SEARCH_TOOL = {
        "type": "web_search_20250305",
        "name": "web_search",
    }

    def __init__(self, api_key: str, model: str = "claude-haiku-4-5"):
        super().__init__(api_key, model)
        self.client = anthropic.Anthropic(api_key=api_key)

    async def generate(
        self,
        messages: list[LLMMessage],
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        enable_web_search: bool = False,
    ) -> LLMResponse:
        """Generate a response from Claude, optionally with native web search."""
        system_message = None
        user_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                user_messages.append({"role": msg.role, "content": msg.content})

        kwargs = dict(
            model=self.model,
            max_tokens=max_tokens or 4096,
            temperature=temperature,
            system=system_message,
            messages=user_messages,
        )
        if enable_web_search:
            try:
                import anthropic as _anthropic
                major = int(_anthropic.__version__.split(".")[0])
                minor = int(_anthropic.__version__.split(".")[1])
                if (major, minor) >= (0, 28):
                    kwargs["tools"] = [self.WEB_SEARCH_TOOL]
            except Exception:
                pass  # gracefully skip web search if SDK is too old

        response = self.client.messages.create(**kwargs)

        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        estimated_cost = self.estimate_cost(input_tokens, output_tokens)

        # Assemble text reply and extract any web-search results
        text_parts: List[str] = []
        web_sources: List[dict] = []

        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_result":
                # web_search tool returns a list of result objects
                for item in (block.content or []):
                    if isinstance(item, dict):
                        web_sources.append({
                            "title": item.get("title", ""),
                            "url": item.get("url", ""),
                            "snippet": item.get("encrypted_content", item.get("snippet", "")),
                        })

        return LLMResponse(
            content="\n".join(text_parts) or "",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=self.model,
            provider=self.get_provider_name(),
            estimated_cost_usd=estimated_cost,
            web_sources=web_sources,
        )

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        pricing = self.PRICING.get(self.model, self.PRICING["claude-3-5-sonnet-20241022"])
        return (input_tokens / 1_000_000) * pricing["input"] + \
               (output_tokens / 1_000_000) * pricing["output"]

    def get_model_name(self) -> str:
        return self.model

    def get_provider_name(self) -> str:
        return "anthropic"
