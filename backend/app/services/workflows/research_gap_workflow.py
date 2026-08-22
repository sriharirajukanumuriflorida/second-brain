"""
Research Gap Analysis workflow.
"""
from typing import Dict, Any
from app.services.workflows.base import BaseWorkflow
from app.services.llm.base import LLMMessage
from app.services.prompts.research_gap import RESEARCH_GAP_SYSTEM_PROMPT, RESEARCH_GAP_USER_PROMPT
from app.utils.logger import log_event


class ResearchGapWorkflow(BaseWorkflow):
    """Research Gap Analysis workflow."""

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Research Gap Analysis workflow."""
        current_capabilities = context.get("current_capabilities", "Vault indexing, keyword search, LLM workflows, GitHub integration")
        known_limitations = context.get("known_limitations", "No semantic search yet, limited to keyword search")
        context_query = context.get("context_query", "architecture limitations gaps")

        # Retrieve relevant notes
        notes = self.retrieve_context_notes(context_query, limit=15)
        notes_context = self.format_notes_as_context(notes)

        # Build messages
        messages = [
            LLMMessage(role="system", content=RESEARCH_GAP_SYSTEM_PROMPT),
            LLMMessage(
                role="user",
                content=RESEARCH_GAP_USER_PROMPT.format(
                    notes_context=notes_context,
                    current_capabilities=current_capabilities,
                    known_limitations=known_limitations
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
        return "research-gap-analysis"
