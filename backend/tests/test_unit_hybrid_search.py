"""
Unit tests for hybrid search: keyword search, body-content matching, graceful
semantic fallback on SQLite, and the score-blending logic.
"""
import json
from app.models import Note, EmbeddingChunk
from app.services.search.hybrid_search import HybridSearchService


def _add_note(db, title, folder="03 Permanent Notes", frontmatter="", archived=False):
    note = Note(
        path=f"{folder}/{title}.md",
        title=title,
        file_hash="h",
        folder=folder,
        frontmatter=frontmatter,
        tags=json.dumps([]),
        is_archived=archived,
    )
    db.add(note)
    db.commit()
    return note


def _add_chunk(db, note, content, chunk_index=0):
    chunk = EmbeddingChunk(
        note_id=note.id,
        chunk_index=chunk_index,
        content=content,
        file_hash="h",
        chunk_hash=f"c{chunk_index}",
        is_stale=False,
    )
    db.add(chunk)
    db.commit()
    return chunk


class TestKeywordSearch:
    def test_matches_title(self, db_session):
        _add_note(db_session, "RAG Evaluation Metrics")
        _add_note(db_session, "Vector Database Tradeoffs")
        svc = HybridSearchService(db_session)
        results = svc.search("RAG", limit=10)
        titles = [r["title"] for r in results]
        assert "RAG Evaluation Metrics" in titles
        assert "Vector Database Tradeoffs" not in titles

    def test_excludes_archived(self, db_session):
        _add_note(db_session, "Archived RAG Note", archived=True)
        svc = HybridSearchService(db_session)
        assert svc.search("RAG", limit=10) == []

    def test_folder_filter(self, db_session):
        _add_note(db_session, "RAG A", folder="03 Permanent Notes")
        _add_note(db_session, "RAG B", folder="13 Governance")
        svc = HybridSearchService(db_session)
        results = svc.search("RAG", folder="13 Governance", limit=10)
        assert [r["title"] for r in results] == ["RAG B"]


class TestBodyContentSearch:
    def test_matches_body_via_chunk_content(self, db_session):
        """A term only in the note body (not title/frontmatter) is found via chunks."""
        note = _add_note(db_session, "Vector Databases")
        _add_chunk(db_session, note, "This note discusses the HNSW indexing algorithm in depth.")
        svc = HybridSearchService(db_session)
        results = svc.search("HNSW", limit=10)
        assert any(r["id"] == note.id for r in results)

    def test_title_match_outranks_body_match(self, db_session):
        """Title hits (1.0) should rank above body-only hits (0.7)."""
        title_hit = _add_note(db_session, "HNSW Overview")
        body_hit = _add_note(db_session, "Some Other Note")
        _add_chunk(db_session, body_hit, "Buried mention of HNSW in the body.")
        svc = HybridSearchService(db_session)
        results = svc.search("HNSW", limit=10)
        ids = [r["id"] for r in results]
        assert ids.index(title_hit.id) < ids.index(body_hit.id)

    def test_body_scan_fallback_reads_filesystem(self, db_session, tmp_path, monkeypatch):
        """Notes with no chunks fall back to a filesystem body scan."""
        from app.config import settings
        monkeypatch.setattr(settings, "vault_path", tmp_path)

        note = _add_note(db_session, "Filesystem Note")
        note_file = tmp_path / note.path
        note_file.parent.mkdir(parents=True, exist_ok=True)
        note_file.write_text("# Filesystem Note\n\nContains the term quokka only in the body.", encoding="utf-8")

        svc = HybridSearchService(db_session)
        results = svc.search("quokka", limit=10)
        assert any(r["id"] == note.id for r in results)


class TestSemanticFallback:
    def test_semantic_unavailable_on_sqlite(self, db_session):
        """No pgvector on SQLite -> availability is False, no crash."""
        svc = HybridSearchService(db_session)
        assert svc.semantic_search_available() is False

    def test_search_with_embedding_falls_back_to_keyword(self, db_session):
        """Passing an embedding on SQLite must not error; returns keyword hits."""
        _add_note(db_session, "RAG Evaluation Metrics")
        svc = HybridSearchService(db_session)
        results = svc.search("RAG", limit=10, query_embedding=[0.1] * 1536)
        assert any(r["title"] == "RAG Evaluation Metrics" for r in results)
        assert all(r["search_type"] == "keyword" for r in results)


class TestBlend:
    def test_hybrid_merges_and_weights(self, db_session):
        svc = HybridSearchService(db_session)
        keyword = [{"id": 1, "path": "a", "title": "A", "folder": "f", "score": 1.0, "search_type": "keyword"}]
        semantic = [
            {"id": 1, "path": "a", "title": "A", "folder": "f", "score": 0.8, "search_type": "semantic"},
            {"id": 2, "path": "b", "title": "B", "folder": "f", "score": 0.9, "search_type": "semantic"},
        ]
        blended = svc._blend(keyword, semantic, keyword_weight=0.5, semantic_weight=0.5, limit=10)
        by_id = {r["id"]: r for r in blended}
        # note 1 present in both -> hybrid, score = 0.5*1.0 + 0.5*0.8 = 0.9
        assert by_id[1]["search_type"] == "hybrid"
        assert abs(by_id[1]["score"] - 0.9) < 1e-9
        # note 2 semantic-only -> score = 0.5*0.9 = 0.45
        assert abs(by_id[2]["score"] - 0.45) < 1e-9
        # ranked descending
        assert [r["id"] for r in blended] == [1, 2]
