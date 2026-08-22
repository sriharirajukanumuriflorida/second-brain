"""
FDE Solution Brief workflow.
"""
from typing import Dict, Any
from app.services.workflows.base import BaseWorkflow
from app.services.llm.base import LLMMessage
from app.services.prompts.solution_brief import SOLUTION_BRIEF_SYSTEM_PROMPT, SOLUTION_BRIEF_USER_PROMPT
from app.utils.logger import log_event


class SolutionBriefWorkflow(BaseWorkflow):
    """FDE Solution Brief workflow."""

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Solution Brief workflow."""
        problem = context.get("problem", "")
        context_query = context.get("context_query", "")
        constraints = context.get("constraints", "Not specified")
        stakeholders = context.get("stakeholders", "Not specified")

        # Retrieve relevant notes for context
        notes = self.retrieve_context_notes(context_query, limit=5)
        notes_context = self.format_notes_as_context(notes)

        # Build messages
        messages = [
            LLMMessage(role="system", content=SOLUTION_BRIEF_SYSTEM_PROMPT),
            LLMMessage(
                role="user",
                content=SOLUTION_BRIEF_USER_PROMPT.format(
                    problem=problem,
                    context=notes_context,
                    constraints=constraints,
                    stakeholders=stakeholders
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
        return "solution-brief"
