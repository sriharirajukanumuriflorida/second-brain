"""
Unit tests for embedding activation during sync (Tier 1.1).

Covers:
- IndexService.index_vault returns changed_paths (created/updated only).
- embed_changed_notes replaces a note's old chunks and is best-effort.
"""
import asyncio
from pathlib import Path

import pytest

from app.models import Note, EmbeddingChunk
from app.services.index_service import IndexService
from app.services.embeddings.base import BaseEmbeddingProvider
from app.services.embeddings.embedding_service import EmbeddingService
from app.api.sync import embed_changed_notes


class FakeEmbeddingProvider(BaseEmbeddingProvider):
    """Deterministic offline embedding provider for tests."""

    def __init__(self):
        super().__init__(api_key="test", model="fake-embed")
        self.calls = 0

    async def generate_embeddings(self, texts):
        self.calls += 1
        return [[0.1, 0.2, 0.3] for _ in texts]

    def get_embedding_dimension(self):
        return 3

    def estimate_cost(self, token_count):
        return 0.0

    def get_model_name(self):
        return "fake-embed"

    def get_provider_name(self):
        return "fake"


def _write_note(vault: Path, rel_path: str, body: str):
    file_path = vault / rel_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(body, encoding="utf-8")
    return file_path


def test_index_vault_reports_changed_paths(tmp_path, db_session):
    """First index reports all notes; re-index with no changes reports none."""
    vault = tmp_path / "vault"
    vault.mkdir()
    _write_note(vault, "03 Permanent Notes/alpha.md", "# Alpha\n\nSome content about alpha.")

    stats = IndexService(db_session, vault).index_vault()
    assert stats["indexed"] == 1
    assert "03 Permanent Notes/alpha.md" in stats["changed_paths"]

    # Re-index unchanged -> skipped, no changed paths.
    stats2 = IndexService(db_session, vault).index_vault()
    assert stats2["skipped"] == 1
    assert stats2["changed_paths"] == []


def test_index_vault_reports_updated_note(tmp_path, db_session):
    """Editing a note's body surfaces it in changed_paths on re-index."""
    vault = tmp_path / "vault"
    vault.mkdir()
    note_path = _write_note(vault, "03 Permanent Notes/beta.md", "# Beta\n\nOriginal.")
    IndexService(db_session, vault).index_vault()

    note_path.write_text("# Beta\n\nEdited content.", encoding="utf-8")
    stats = IndexService(db_session, vault).index_vault()
    assert stats["updated"] == 1
    assert "03 Permanent Notes/beta.md" in stats["changed_paths"]


def test_embed_changed_notes_creates_chunks(tmp_path, db_session, monkeypatch):
    """embed_changed_notes generates chunks for changed notes."""
    vault = tmp_path / "vault"
    vault.mkdir()
    _write_note(vault, "03 Permanent Notes/gamma.md", "# Gamma\n\nContent for gamma note.")
    stats = IndexService(db_session, vault).index_vault()

    # Force the sync helper to use the fake provider.
    monkeypatch.setattr(
        "app.api.sync._build_embedding_provider", lambda: FakeEmbeddingProvider()
    )

    embedded = asyncio.get_event_loop().run_until_complete(
        embed_changed_notes(db_session, vault, stats["changed_paths"])
    )
    assert embedded == 1
    assert db_session.query(EmbeddingChunk).count() >= 1


def test_regenerate_replaces_old_chunks(tmp_path, db_session):
    """Re-embedding a note deletes its prior chunks (no orphans)."""
    vault = tmp_path / "vault"
    vault.mkdir()
    _write_note(vault, "03 Permanent Notes/delta.md", "# Delta\n\nFirst version body text.")
    IndexService(db_session, vault).index_vault()
    note = db_session.query(Note).filter(Note.path == "03 Permanent Notes/delta.md").first()

    service = EmbeddingService(db_session, FakeEmbeddingProvider())
    loop = asyncio.get_event_loop()
    v1 = "# Delta\n\nFirst version unique-marker-alpha body text."
    v2 = "# Delta\n\nSecond version unique-marker-omega with different body text."

    loop.run_until_complete(service.generate_embeddings_for_note(note, v1))
    count_after_v1 = db_session.query(EmbeddingChunk).filter(EmbeddingChunk.note_id == note.id).count()
    assert count_after_v1 >= 1

    # Regenerate with different content; old chunks must be replaced, not accumulated.
    loop.run_until_complete(service.generate_embeddings_for_note(note, v2))
    chunks = db_session.query(EmbeddingChunk).filter(EmbeddingChunk.note_id == note.id).all()

    # No accumulation: replacing content shouldn't grow the chunk set for the note.
    assert len(chunks) == count_after_v1
    # And no chunk retains the old version's unique marker.
    joined = "\n".join(c.content for c in chunks)
    assert "unique-marker-alpha" not in joined
    assert "unique-marker-omega" in joined


def test_embed_changed_notes_skips_without_key(tmp_path, db_session, monkeypatch):
    """No embedding key -> helper no-ops rather than erroring the sync."""
    vault = tmp_path / "vault"
    vault.mkdir()
    _write_note(vault, "03 Permanent Notes/epsilon.md", "# Epsilon\n\nBody.")
    stats = IndexService(db_session, vault).index_vault()

    monkeypatch.setattr("app.api.sync._build_embedding_provider", lambda: None)
    embedded = asyncio.get_event_loop().run_until_complete(
        embed_changed_notes(db_session, vault, stats["changed_paths"])
    )
    assert embedded == 0
    assert db_session.query(EmbeddingChunk).count() == 0
