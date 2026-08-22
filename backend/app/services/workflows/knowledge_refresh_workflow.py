"""
Knowledge Refresh workflow.
"""
from typing import Dict, Any
from datetime import datetime, timedelta
from app.services.workflows.base import BaseWorkflow
from app.services.llm.base import LLMMessage
from app.services.prompts.knowledge_refresh import KNOWLEDGE_REFRESH_SYSTEM_PROMPT, KNOWLEDGE_REFRESH_USER_PROMPT
from app.utils.logger import log_event
from app.models import Note


class KnowledgeRefreshWorkflow(BaseWorkflow):
    """Knowledge Refresh workflow."""

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Knowledge Refresh workflow."""
        time_period = context.get("time_period", "30 days")

        # Retrieve recent notes
        cutoff_date = datetime.now() - timedelta(days=30)
        notes = self.db.query(Note).filter(
            Note.created_at >= cutoff_date
        ).all()

        notes_context = self.format_notes_as_context(notes)

        # Build messages
        messages = [
            LLMMessage(role="system", content=KNOWLEDGE_REFRESH_SYSTEM_PROMPT),
            LLMMessage(
                role="user",
                content=KNOWLEDGE_REFRESH_USER_PROMPT.format(
                    notes_context=notes_context,
                    time_period=time_period,
                    note_count=len(notes)
                )
            )
        ]

        # Generate response
        response = await self.llm_provider.generate(messages)

        # Log workflow execution
        log_event(self.db, "workflow.completed", {
            "workflow": self.get_workflow_name(),
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "cost_usd": response.estimated_cost_usd,
            "model": response.model
        })

        return {
            "content": response.content,
            "source_notes": [note.path for note in notes],
            "llm_calls": 1,
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
            "estimated_cost_usd": response.estimated_cost_usd,
            "model": response.model,
            "provider": response.provider
        }

    def get_workflow_name(self) -> str:
        return "knowledge-refresh"
