"""
Compaction / LLM-wiki workflow.

Implements the Karpathy "LLM wiki" pattern: select immutable source notes on a
topic and compile them into ONE derived, cross-linked wiki page. Sources are
never mutated; the output is written under 14 Agent Outputs/ and merged via PR
(reusing GitHubBranchService), so it slots into the existing read-before-write,
PR-reviewed phase discipline.
"""
from typing import Dict, Any, List
from app.services.workflows.base import BaseWorkflow
from app.services.llm.base import LLMMessage
from app.services.search.hybrid_search import HybridSearchService
from app.services.prompts.compaction import (
    COMPACTION_SYSTEM_PROMPT,
    COMPACTION_USER_PROMPT,
)
from app.config import settings
from app.utils.logger import log_event
from app.models import Note

# Bound how many source notes and how much of each body we send to the LLM,
# to keep a single compaction pass cost-predictable.
_MAX_SOURCE_NOTES = 12
_MAX_BODY_CHARS = 6000


class CompactionWorkflow(BaseWorkflow):
    """Compile immutable source notes into one derived wiki page."""

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        topic = (context.get("context_query") or context.get("content") or "").strip()
        if not topic:
            raise ValueError("Compaction requires a topic (context_query or content).")

        source_notes = self._select_sources(topic)
        notes_context = self._format_bodies(source_notes)

        messages = [
            LLMMessage(role="system", content=COMPACTION_SYSTEM_PROMPT),
            LLMMessage(
                role="user",
                content=COMPACTION_USER_PROMPT.format(
                    topic=topic,
                    notes_context=notes_context,
                    note_count=len(source_notes),
                ),
            ),
        ]

        response = await self.llm_provider.generate(messages)

        log_event(self.db, "workflow.completed", {
            "workflow": self.get_workflow_name(),
            "topic": topic,
            "source_count": len(source_notes),
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "cost_usd": response.estimated_cost_usd,
            "model": response.model,
        })

        return {
            "content": response.content,
            "source_notes": [note.path for note in source_notes],
            "llm_calls": 1,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "estimated_cost_usd": response.estimated_cost_usd,
            "model": response.model,
            "provider": response.provider,
        }

    def get_workflow_name(self) -> str:
        return "compaction"

    def _select_sources(self, topic: str) -> List[Note]:
        """Pick the source notes for a topic via hybrid search.

        Uses keyword+body matching (semantic too when pgvector is live). Falls
        back to nothing rather than erroring if search returns empty — the LLM
        is then told the sources are thin.
        """
        search = HybridSearchService(self.db)
        hits = search.search(query=topic, limit=_MAX_SOURCE_NOTES)
        ids = [h["id"] for h in hits]
        if not ids:
            return []
        notes = self.db.query(Note).filter(Note.id.in_(ids)).all()
        # Preserve search rank order.
        by_id = {n.id: n for n in notes}
        return [by_id[i] for i in ids if i in by_id]

    def _format_bodies(self, notes: List[Note]) -> str:
        """Read note bodies from VAULT_PATH and format them for the prompt.

        Bodies are read on demand (filesystem-on-demand design) and truncated
        to _MAX_BODY_CHARS each. A note whose file can't be read is included by
        title only, so one bad file doesn't sink the pass.
        """
        if not notes:
            return "No source notes were found for this topic."

        parts = []
        for note in notes:
            body = ""
            try:
                with open(settings.vault_path / note.path, "r", encoding="utf-8") as f:
                    body = f.read()[:_MAX_BODY_CHARS]
            except OSError:
                body = "(body unavailable)"
            parts.append(f"### Source: {note.title}\n(path: {note.path})\n\n{body}\n")
        return "\n---\n".join(parts)
