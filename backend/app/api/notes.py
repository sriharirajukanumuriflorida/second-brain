"""
Notes endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, text
from app.database import get_db
from app.schemas import NoteResponse, RelatedNote
from app.models import Note
from app.utils.auth import require_read_access, Principal
from typing import List
import json

router = APIRouter()

obsidian_folder_filter = or_(*[Note.folder.like(f"{digit}%") for digit in "0123456789"])
excluded_folder_filter = Note.folder != "14 Agent Outputs"


@router.get("/notes", response_model=List[NoteResponse])
async def list_notes(
    folder: str = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_read_access),
):
    """List all notes."""
    query = (
        db.query(Note)
        .filter(Note.is_archived == False)
        .filter(obsidian_folder_filter)
        .filter(excluded_folder_filter)
    )

    if folder:
        query = query.filter(Note.folder == folder)

    notes = query.limit(limit).all()

    return [
        NoteResponse(
            id=note.id,
            path=note.path,
            title=note.title,
            tags=json.loads(note.tags) if note.tags else [],
            backlinks=json.loads(note.backlinks) if note.backlinks else [],
            folder=note.folder,
            created_at=note.created_at,
            updated_at=note.updated_at,
            last_indexed_at=note.last_indexed_at
        )
        for note in notes
    ]


@router.get("/notes/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_read_access),
):
    """Get note by ID."""
    note = db.query(Note).filter(Note.id == note_id).first()

    if not note or not note.folder[:1].isdigit() or note.folder == "14 Agent Outputs":
        raise HTTPException(status_code=404, detail="Note not found")

    return NoteResponse(
        id=note.id,
        path=note.path,
        title=note.title,
        tags=json.loads(note.tags) if note.tags else [],
        backlinks=json.loads(note.backlinks) if note.backlinks else [],
        folder=note.folder,
        created_at=note.created_at,
        updated_at=note.updated_at,
        last_indexed_at=note.last_indexed_at
    )


@router.get("/notes/{note_id}/related", response_model=List[RelatedNote])
async def get_related_notes(
    note_id: int,
    limit: int = 5,
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_read_access),
):
    """Return notes semantically similar to this one (Smart-Connections style).

    kNN over pgvector: for every chunk of the target note, find the nearest
    chunks belonging to *other* eligible notes, then keep the best similarity
    per note. Requires Postgres + embeddings; returns [] on SQLite / when the
    note has no embeddings, so the UI degrades gracefully.
    """
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note or not note.folder[:1].isdigit() or note.folder == "14 Agent Outputs":
        raise HTTPException(status_code=404, detail="Note not found")

    if "postgres" not in str(db.bind.url):
        return []

    obsidian_clause = (
        "AND (" + " OR ".join([f"n.folder LIKE '{digit}%'" for digit in "0123456789"]) + ") "
        "AND n.folder != '14 Agent Outputs'"
    )
    sql = text(f"""
        SELECT n.id AS note_id, n.path, n.title, n.folder,
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
        GROUP BY n.id, n.path, n.title, n.folder
        ORDER BY distance ASC
        LIMIT :limit
    """)

    try:
        rows = db.execute(sql, {"note_id": note_id, "limit": limit}).mappings().all()
    except Exception:
        # Missing embedding_vec column or other pgvector issue -> degrade to empty.
        return []

    return [
        RelatedNote(
            id=r["note_id"],
            path=r["path"],
            title=r["title"],
            folder=r["folder"],
            score=max(0.0, 1.0 - (float(r["distance"]) / 2.0)),
        )
        for r in rows
    ]
