"""
Output generation service with metadata.
"""
from typing import Dict, Any
from datetime import datetime, timezone
import yaml


class OutputService:
    """Service for generating outputs with required metadata."""

    def generate_output(
        self,
        workflow: str,
        content: str,
        source_notes: list[str],
        llm_calls: int,
        input_tokens: int,
        output_tokens: int,
        estimated_cost_usd: float,
        model: str,
        provider: str
    ) -> str:
        """Generate output with required metadata front matter."""

        # Create metadata
        metadata = {
            "type": "agent-output",
            "workflow": workflow,
            "status": "draft",
            "source_notes": source_notes,
            "created": datetime.now(timezone.utc).isoformat(),
            "model": model,
            "llm_calls": llm_calls,
            "estimated_input_tokens": input_tokens,
            "estimated_output_tokens": output_tokens,
            "estimated_cost_usd": estimated_cost_usd,
            "approval_status": "pending",
            "tags": ["fde-agent", "generated"]
        }

        # Format as YAML front matter
        frontmatter_yaml = yaml.dump(metadata, default_flow_style=False)

        # Combine front matter and content
        output = f"---\n{frontmatter_yaml}---\n\n{content}"

        return output

    def generate_filename(self, workflow: str) -> str:
        """Generate filename for output."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        return f"{workflow}-{timestamp}.md"
