"""
Notes endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.schemas import NoteResponse
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
