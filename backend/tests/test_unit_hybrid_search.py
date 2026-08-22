"""
Unit tests for hybrid search: keyword search, graceful semantic fallback on
SQLite, and the score-blending logic.
"""
import json
from app.models import Note
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
