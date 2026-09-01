"""
Unit tests for the MCP vault tool logic (Tier 2.5).

Tests the transport-agnostic tools in mcp_server.tools directly — no MCP
stdio layer required.
"""
import json

from app.models import Note
from mcp_server import tools


def _add_note(db, title, folder="03 Permanent Notes"):
    note = Note(
        path=f"{folder}/{title}.md",
        title=title,
        file_hash="h",
        folder=folder,
        tags=json.dumps([]),
        frontmatter="",
        is_archived=False,
    )
    db.add(note)
    db.commit()
    return note


class TestSearchNotes:
    def test_returns_matches(self, db_session):
        _add_note(db_session, "RAG Evaluation Metrics")
        results = tools.search_notes(db_session, "RAG", limit=5)
        assert any(r["title"] == "RAG Evaluation Metrics" for r in results)
        assert all({"id", "path", "title", "score"} <= set(r) for r in results)


class TestFetchNote:
    def test_by_id_reads_body(self, db_session, tmp_path, monkeypatch):
        from app.config import settings
        monkeypatch.setattr(settings, "vault_path", tmp_path)

        note = _add_note(db_session, "Body Note")
        note_file = tmp_path / note.path
        note_file.parent.mkdir(parents=True, exist_ok=True)
        note_file.write_text("# Body Note\n\nThe body content.", encoding="utf-8")

        result = tools.fetch_note(db_session, note_id=note.id)
        assert result["title"] == "Body Note"
        assert "The body content." in result["body"]

    def test_by_path(self, db_session, tmp_path, monkeypatch):
        from app.config import settings
        monkeypatch.setattr(settings, "vault_path", tmp_path)
        note = _add_note(db_session, "Path Note")
        result = tools.fetch_note(db_session, path=note.path)
        assert result["id"] == note.id

    def test_missing_returns_error(self, db_session):
        assert "error" in tools.fetch_note(db_session, note_id=99999)

    def test_agent_outputs_hidden(self, db_session):
        note = _add_note(db_session, "Generated", folder="14 Agent Outputs")
        assert "error" in tools.fetch_note(db_session, note_id=note.id)

    def test_requires_an_arg(self, db_session):
        assert "error" in tools.fetch_note(db_session)


class TestRelatedNotes:
    def test_empty_on_sqlite(self, db_session):
        note = _add_note(db_session, "Some Note")
        assert tools.related_notes(db_session, note.id) == []

    def test_missing_note(self, db_session):
        assert tools.related_notes(db_session, 99999) == []
