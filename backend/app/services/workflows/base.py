"""
Base workflow class.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.services.llm.base import LLMMessage, LLMResponse
from app.models import Note


class BaseWorkflow(ABC):
    """Base class for workflows."""

    def __init__(self, db: Session, llm_provider):
        self.db = db
        self.llm_provider = llm_provider

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the workflow."""
        pass

    @abstractmethod
    def get_workflow_name(self) -> str:
        """Get the workflow name."""
        pass

    def retrieve_context_notes(self, query: str, limit: int = 10) -> List[Note]:
        """Retrieve relevant notes for context."""
        # Simple keyword search for now
        # In Phase 5, this will use semantic search
        from app.models import Note
        search_pattern = f"%{query}%"
        notes = self.db.query(Note).filter(
            (Note.title.ilike(search_pattern)) |
            (Note.frontmatter.ilike(search_pattern))
        ).limit(limit).all()
        return notes

    def format_notes_as_context(self, notes: List[Note]) -> str:
        """Format notes as context string."""
        if not notes:
            return "No relevant notes found."

        context_parts = []
        for note in notes:
            context_parts.append(f"## {note.title}")
            context_parts.append(f"Path: {note.path}")
            context_parts.append(f"Tags: {note.tags}")
            context_parts.append("---")

        return "\n".join(context_parts)
