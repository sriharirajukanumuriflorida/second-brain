"""
OpenAI/Azure OpenAI LLM provider.
"""
from openai import AsyncOpenAI
from typing import Optional, List
from .base import BaseLLMProvider, LLMMessage, LLMResponse


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider using OpenAI API."""

    PRICING = {
        "gpt-4o":           {"input": 5.0,  "output": 15.0},
        "gpt-4o-mini":      {"input": 0.15, "output": 0.60},
        "gpt-4-turbo":      {"input": 10.0, "output": 30.0},
        "gpt-3.5-turbo":    {"input": 0.5,  "output": 1.5},
    }

    def __init__(self, api_key: str, model: str = "gpt-4o", base_url: Optional[str] = None):
        super().__init__(api_key, model)
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def generate(
        self,
        messages: list[LLMMessage],
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        enable_web_search: bool = False,
    ) -> LLMResponse:
        """Generate a response from OpenAI, optionally with native web search."""
        openai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

        kwargs = dict(
            model=self.model,
            messages=openai_messages,
            max_tokens=max_tokens or 4096,
            temperature=temperature,
        )
        if enable_web_search:
            kwargs["tools"] = [{"type": "web_search_preview"}]

        response = await self.client.chat.completions.create(**kwargs)

        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        estimated_cost = self.estimate_cost(input_tokens, output_tokens)

        # Collect reply text and any web search annotations
        message = response.choices[0].message
        content = message.content or ""
        web_sources: List[dict] = []

        # OpenAI web search returns url_citation annotations on the message
        annotations = getattr(message, "annotations", None) or []
        for ann in annotations:
            if getattr(ann, "type", "") == "url_citation":
                ref = ann.url_citation
                web_sources.append({
                    "title": getattr(ref, "title", ""),
                    "url": getattr(ref, "url", ""),
                    "snippet": "",
                })

        return LLMResponse(
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=self.model,
            provider=self.get_provider_name(),
            estimated_cost_usd=estimated_cost,
            web_sources=web_sources,
        )

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        pricing = self.PRICING.get(self.model, self.PRICING["gpt-4o"])
        return (input_tokens / 1_000_000) * pricing["input"] + \
               (output_tokens / 1_000_000) * pricing["output"]

    def get_model_name(self) -> str:
        return self.model

    def get_provider_name(self) -> str:
        return "openai"
