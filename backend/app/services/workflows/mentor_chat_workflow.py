"""
Mentor Chat workflow.

Orchestrates:
  1. Hybrid-search vault for relevant notes (TokenBudgetService.select_context)
  2. Compress old history (TokenBudgetService.summarize_history)
  3. Route to cheap/powerful model (TokenBudgetService.route_model)
  5. Assemble system prompt + vault context + history + user message
  6. Call LLM with native web_search tool enabled
  7. Return reply + source_notes + web_sources
"""
import json
import re
from typing import Dict, Any, List

from sqlalchemy.orm import Session

from app.models import EmbeddingChunk
from app.services.workflows.base import BaseWorkflow
from app.services.llm.base import LLMMessage
from app.services.search.hybrid_search import HybridSearchService
from app.services.token_budget import TokenBudgetService
from app.services.prompts.mentor_chat import MENTOR_SYSTEM_PROMPT, MENTOR_USER_TEMPLATE
from app.utils.logger import log_event


MIN_CONTEXT_SCORE = 0.3


class MentorChatWorkflow(BaseWorkflow):
    """LLM mentor chat workflow with vault RAG and optional web search."""

    def __init__(self, db: Session, llm_provider):
        super().__init__(db, llm_provider)
        self.search_svc = HybridSearchService(db)
        self.budget_svc = TokenBudgetService(db)

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        message: str = context["message"]
        history: List[dict] = context.get("history", [])
        enable_web_search: bool = context.get("enable_web_search", True)

        # 1. Search vault for relevant notes
        raw_results = self._retrieve(message, context.get("query_embedding"))
        self._attach_content(raw_results, message)

        # 2. Trim context to token budget. Blended semantic scores top out near
        # 0.5, so the floor is low; tune it against real questions.
        selected = self.budget_svc.select_context(raw_results, max_tokens=2000, min_score=MIN_CONTEXT_SCORE)
        source_notes = [n["path"] for n in selected]

        # Reply cache intentionally disabled: its key ignored user, history and
        # model, so replies could leak across conversations.

        # 4. Optionally route to cheaper model for simple queries
        provider_name = self.llm_provider.get_provider_name()
        cheap_model = self.budget_svc.route_model(message, provider_name)
        if cheap_model:
            # Swap model temporarily
            original_model = self.llm_provider.model
            self.llm_provider.model = cheap_model
        else:
            original_model = None

        try:
            # 5. Compress history
            compressed = await self.budget_svc.summarize_history(
                history, keep_recent=4, llm_provider=self.llm_provider
            )

            # 6. Build vault context string
            vault_context = self._format_vault_context(selected)

            # 7. Assemble messages
            messages = [
                LLMMessage(
                    role="system",
                    content=MENTOR_SYSTEM_PROMPT.format(vault_context=vault_context),
                )
            ]
            for h in compressed:
                messages.append(LLMMessage(role=h["role"], content=h["content"]))
            messages.append(LLMMessage(role="user", content=MENTOR_USER_TEMPLATE.format(message=message)))

            # 8. Call LLM with web search enabled
            response = await self.llm_provider.generate(
                messages,
                max_tokens=2048,
                temperature=0.7,
                enable_web_search=enable_web_search,
            )

        finally:
            # Restore original model
            if original_model:
                self.llm_provider.model = original_model

        log_event(self.db, "chat.completed", {
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "model": response.model,
            "source_notes": len(source_notes),
            "web_sources": len(response.web_sources),
        })

        return {
            "reply": response.content,
            "source_notes": source_notes,
            "web_sources": response.web_sources,
            "model": response.model,
            "provider": response.provider,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "estimated_cost_usd": response.estimated_cost_usd,
            "cached": False,
        }

    def _retrieve(self, message: str, query_embedding) -> List[dict]:
        """Whole-message search first. Keyword search substring-matches the whole
        query, so a natural-language question rarely hits; when nothing comes
        back, retry per significant term (a keyword-only fallback)."""
        results = self.search_svc.search(query=message, limit=10, query_embedding=query_embedding)
        if results:
            return results
        merged: Dict[int, dict] = {}
        for term in list(dict.fromkeys(re.findall(r"\w{4,}", message.lower())))[:6]:
            for row in self.search_svc.search(query=term, limit=10):
                merged.setdefault(row["id"], row)
        return sorted(merged.values(), key=lambda r: r["score"], reverse=True)[:10]

    def _attach_content(self, notes: List[dict], query: str, max_chunks: int = 2) -> None:
        """Put the note's most query-relevant chunk text on each result so the
        model sees excerpts, not just titles. Notes without chunks stay title-only."""
        terms = set(re.findall(r"\w{4,}", query.lower()))
        for note in notes:
            chunks = (
                self.db.query(EmbeddingChunk)
                .filter(EmbeddingChunk.note_id == note["id"])
                .order_by(EmbeddingChunk.chunk_index)
                .all()
            )
            if not chunks:
                continue
            ranked = sorted(
                chunks,
                key=lambda c: (-len(terms & set(re.findall(r"\w{4,}", c.content.lower()))), c.chunk_index),
            )
            note["content"] = "\n…\n".join(c.content for c in ranked[:max_chunks])

    def _format_vault_context(self, notes: List[dict]) -> str:
        if not notes:
            return "No relevant vault notes found for this query."
        parts = []
        for note in notes:
            parts.append(f"### {note.get('title', note['path'])}")
            parts.append(f"*Path: {note['path']}*")
            if note.get("content"):
                parts.append(note["content"][:1000])
            parts.append("")
        return "\n".join(parts)

    def get_workflow_name(self) -> str:
        return "mentor-chat"
