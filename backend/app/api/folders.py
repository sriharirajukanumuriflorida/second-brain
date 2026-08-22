"""
Folders endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import FolderResponse
from app.models import Note
from app.utils.auth import require_read_access, Principal
from sqlalchemy import func

router = APIRouter()


@router.get("/folders", response_model=List[FolderResponse])
async def list_folders(
    db: Session = Depends(get_db),
    principal: Principal = Depends(require_read_access),
):
    """List all folders with note counts."""
    folders = db.query(
        Note.folder,
        func.count(Note.id).label("note_count")
    ).filter(
        Note.is_archived == False
    ).group_by(Note.folder).all()

    return [
        FolderResponse(name=folder, note_count=count)
        for folder, count in folders
    ]
