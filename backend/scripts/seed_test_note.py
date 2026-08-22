"""
Insert one test note into the local DB so read-only access can be demoed
without a full GitHub vault sync. Local/testing convenience only.

Usage (from backend/):  python -m scripts.seed_test_note
"""
import json
from app.database import SessionLocal, init_db
from app.models import Note


def main():
    init_db()
    db = SessionLocal()
    try:
        existing = db.query(Note).filter(Note.path == "03 Permanent Notes/Test Note.md").first()
        if existing:
            print("Test note already exists (id=%s)." % existing.id)
            return
        note = Note(
            path="03 Permanent Notes/Test Note.md",
            title="Test Note — RAG Evaluation",
            file_hash="seedhash",
            folder="03 Permanent Notes",
            tags=json.dumps(["rag", "test"]),
            frontmatter="type: permanent-note\ntags: [rag, test]",
            is_archived=False,
        )
        db.add(note)
        db.commit()
        print("Inserted test note (id=%s)." % note.id)
    finally:
        db.close()


if __name__ == "__main__":
    main()
