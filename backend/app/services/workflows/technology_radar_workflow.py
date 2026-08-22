"""
Technology Radar workflow.
"""
from typing import Dict, Any
from app.services.workflows.base import BaseWorkflow
from app.services.llm.base import LLMMessage
from app.services.prompts.technology_radar import TECHNOLOGY_RADAR_SYSTEM_PROMPT, TECHNOLOGY_RADAR_USER_PROMPT
from app.utils.logger import log_event


class TechnologyRadarWorkflow(BaseWorkflow):
    """Technology Radar workflow."""

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Technology Radar workflow."""
        current_stack = context.get("current_stack", "FastAPI, React, SQLite, Claude, OpenAI embeddings")
        context_query = context.get("context_query", "technology architecture")

        # Retrieve relevant notes
        notes = self.retrieve_context_notes(context_query, limit=15)
        notes_context = self.format_notes_as_context(notes)

        # Build messages
        messages = [
            LLMMessage(role="system", content=TECHNOLOGY_RADAR_SYSTEM_PROMPT),
            LLMMessage(
                role="user",
                content=TECHNOLOGY_RADAR_USER_PROMPT.format(
                    notes_context=notes_context,
                    current_stack=current_stack
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
        return "technology-radar"
