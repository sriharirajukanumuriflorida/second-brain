"""
Unit tests for the compaction / LLM-wiki workflow (Tier 2.4).

Covers the workflow class with a fake LLM provider, and the endpoint's
auth/validation guards (which don't require a live LLM or GitHub).
"""
import asyncio
import json

import pytest

from app.models import Note
from app.services.llm.base import BaseLLMProvider, LLMResponse
from app.services.workflows.compaction_workflow import CompactionWorkflow

API = "/api/v1"


class FakeLLMProvider(BaseLLMProvider):
    """Records the prompt it received; returns a canned wiki page."""

    def __init__(self):
        super().__init__(api_key="test", model="fake-llm")
        self.last_messages = None

    async def generate(self, messages, max_tokens=None, temperature=0.7):
        self.last_messages = messages
        return LLMResponse(
            content="## Key Concepts\n\nCompiled page about the topic.",
            input_tokens=100,
            output_tokens=50,
            model="fake-llm",
            provider="fake",
            estimated_cost_usd=0.0,
        )

    def estimate_cost(self, input_tokens, output_tokens):
        return 0.0

    def get_model_name(self):
        return "fake-llm"

    def get_provider_name(self):
        return "fake"


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


class TestCompactionWorkflow:
    def test_compiles_from_source_bodies(self, db_session, tmp_path, monkeypatch):
        from app.config import settings
        monkeypatch.setattr(settings, "vault_path", tmp_path)

        note = _add_note(db_session, "HNSW Indexing")
        note_file = tmp_path / note.path
        note_file.parent.mkdir(parents=True, exist_ok=True)
        note_file.write_text("# HNSW Indexing\n\nHNSW is a graph-based ANN index.", encoding="utf-8")

        llm = FakeLLMProvider()
        wf = CompactionWorkflow(db_session, llm)
        result = asyncio.get_event_loop().run_until_complete(
            wf.execute({"context_query": "HNSW"})
        )

        assert result["source_notes"] == ["03 Permanent Notes/HNSW Indexing.md"]
        assert result["provider"] == "fake"
        # The source body must have been fed into the user prompt.
        user_msg = [m for m in llm.last_messages if m.role == "user"][0]
        assert "graph-based ANN index" in user_msg.content
        assert "HNSW Indexing" in user_msg.content

    def test_requires_topic(self, db_session):
        wf = CompactionWorkflow(db_session, FakeLLMProvider())
        with pytest.raises(ValueError):
            asyncio.get_event_loop().run_until_complete(wf.execute({}))

    def test_thin_sources_still_runs(self, db_session, tmp_path, monkeypatch):
        """No matching notes -> workflow still compiles (LLM told sources are thin)."""
        from app.config import settings
        monkeypatch.setattr(settings, "vault_path", tmp_path)

        wf = CompactionWorkflow(db_session, FakeLLMProvider())
        result = asyncio.get_event_loop().run_until_complete(
            wf.execute({"context_query": "nonexistent topic"})
        )
        assert result["source_notes"] == []
        assert result["content"]


class TestCompactionEndpoint:
    def test_requires_admin(self, client):
        r = client.post(f"{API}/workflows/compaction", json={"topic": "x"})
        assert r.status_code == 403

    def test_empty_topic_rejected(self, client, auth):
        # Empty topic -> workflow raises ValueError -> 400 (no LLM call reached).
        r = client.post(
            f"{API}/workflows/compaction",
            json={"topic": "   "},
            headers=auth["headers"],
        )
        assert r.status_code == 400
