"""
Vault MCP tool logic.

Pure functions over a DB session + the vault filesystem, reusing the same
services the web API uses (HybridSearchService, the notes filters, and the
related-notes kNN). Kept transport-agnostic so it can be unit-tested without
the MCP stdio layer. server.py is the thin MCP wrapper around these.
"""
from typing import List, Dict, Any, Optional
from sqlalchemy import or_, text
from sqlalchemy.orm import Session

from app.models import Note, EmbeddingChunk
from app.services.search.hybrid_search import HybridSearchService
from app.config import settings

# Same vault-only visibility rules the web API enforces: numbered folders,
# excluding generated agent outputs.
_obsidian_folder_filter = or_(*[Note.folder.like(f"{digit}%") for digit in "0123456789"])
_excluded_folder = "14 Agent Outputs"


def search_notes(db: Session, query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search the vault (hybrid keyword + body, semantic when available)."""
    results = HybridSearchService(db).search(query=query, limit=limit)
    return [
        {"id": r["id"], "path": r["path"], "title": r["title"], "score": r.get("score", 0.0)}
        for r in results
    ]


def fetch_note(db: Session, note_id: Optional[int] = None, path: Optional[str] = None) -> Dict[str, Any]:
    """Fetch a single note's metadata + body by id or path.

    Body is read from VAULT_PATH on demand. Returns an ``error`` key when the
    note is missing or not vault-visible, rather than raising.
    """
    if note_id is None and not path:
        return {"error": "provide note_id or path"}

    q = db.query(Note)
    note = q.filter(Note.id == note_id).first() if note_id is not None else q.filter(Note.path == path).first()

    if not note or not note.folder[:1].isdigit() or note.folder == _excluded_folder:
        return {"error": "note not found"}

    body = ""
    try:
        with open(settings.vault_path / note.path, "r", encoding="utf-8") as f:
            body = f.read()
    except OSError:
        body = ""

    return {
        "id": note.id,
        "path": note.path,
        "title": note.title,
        "folder": note.folder,
        "body": body,
    }


def related_notes(db: Session, note_id: int, limit: int = 5) -> List[Dict[str, Any]]:
    """Semantically related notes via pgvector kNN (empty on SQLite/no embeddings)."""
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note or not note.folder[:1].isdigit() or note.folder == _excluded_folder:
        return []
    if "postgres" not in str(db.bind.url):
        return []

    obsidian_clause = (
        "AND (" + " OR ".join([f"n.folder LIKE '{digit}%'" for digit in "0123456789"]) + ") "
        "AND n.folder != '14 Agent Outputs'"
    )
    sql = text(f"""
        SELECT n.id AS note_id, n.path, n.title,
               MIN(other.embedding_vec <=> mine.embedding_vec) AS distance
        FROM embedding_chunks mine
        JOIN embedding_chunks other
          ON other.note_id != mine.note_id
         AND other.embedding_vec IS NOT NULL
         AND other.is_stale = false
        JOIN notes n ON n.id = other.note_id
        WHERE mine.note_id = :note_id
          AND mine.embedding_vec IS NOT NULL
          AND mine.is_stale = false
          AND n.is_archived = false
          {obsidian_clause}
        GROUP BY n.id, n.path, n.title
        ORDER BY distance ASC
        LIMIT :limit
    """)
    try:
        rows = db.execute(sql, {"note_id": note_id, "limit": limit}).mappings().all()
    except Exception:
        return []

    return [
        {
            "id": r["note_id"],
            "path": r["path"],
            "title": r["title"],
            "score": max(0.0, 1.0 - (float(r["distance"]) / 2.0)),
        }
        for r in rows
    ]
