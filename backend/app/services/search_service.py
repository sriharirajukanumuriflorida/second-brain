"""
Keyword search service.
"""
from sqlalchemy.orm import Session
from app.models import Note
from typing import List
import json


class SearchService:
    """Service for keyword search."""

    def __init__(self, db: Session):
        self.db = db

    def search_notes(self, query: str, folder: str = None, limit: int = 20) -> List[dict]:
        """Search notes by keyword."""
        # Build query
        db_query = self.db.query(Note).filter(
            Note.is_archived == False
        )

        if folder:
            db_query = db_query.filter(Note.folder == folder)

        # Simple keyword search in title and content
        # (In production, would use full-text search)
        search_pattern = f"%{query}%"
        db_query = db_query.filter(
            (Note.title.ilike(search_pattern)) |
            (Note.frontmatter.ilike(search_pattern))
        )

        results = db_query.limit(limit).all()

        # Format results
        formatted_results = []
        for note in results:
            formatted_results.append({
                "id": note.id,
                "path": note.path,
                "title": note.title,
                "folder": note.folder,
                "tags": json.loads(note.tags) if note.tags else [],
                "score": 1.0  # Simple scoring for now
            })

        return formatted_results
