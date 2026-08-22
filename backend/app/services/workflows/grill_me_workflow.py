"""
Grill Me Review workflow.
"""
from typing import Dict, Any
from app.services.workflows.base import BaseWorkflow
from app.services.llm.base import LLMMessage
from app.services.prompts.grill_me import GRILL_ME_SYSTEM_PROMPT, GRILL_ME_USER_PROMPT
from app.utils.logger import log_event
import json


class GrillMeWorkflow(BaseWorkflow):
    """Grill Me Review workflow."""

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Grill Me Review workflow."""
        content = context.get("content", "")
        context_query = context.get("context_query", "")

        # Retrieve relevant notes for context
        notes = self.retrieve_context_notes(context_query, limit=5)
        notes_context = self.format_notes_as_context(notes)

        # Build messages
        messages = [
            LLMMessage(role="system", content=GRILL_ME_SYSTEM_PROMPT),
            LLMMessage(
                role="user",
                content=GRILL_ME_USER_PROMPT.format(
                    content=content,
                    context=notes_context
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
        return "grill-me-review"
