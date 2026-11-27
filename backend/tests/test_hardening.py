"""Grounding, embedding safety, quiz failure state, rate limits, health status."""
import pytest

from app.config import settings
from app.models import Note, EmbeddingChunk, User
from app.services.auth.session_service import SessionService
from app.services.embeddings.embedding_service import EmbeddingService
from app.services.llm.base import LLMResponse
from app.services.workflows.mentor_chat_workflow import MentorChatWorkflow
from app.services.workflows.quiz_scoring_workflow import QuizScoringWorkflow, JudgeScoringError
from app.utils.rate_limit import check_rate_limit, reset_rate_limits
from tests.test_unit_sync_embeddings import FakeEmbeddingProvider

API = "/api/v1"


class FakeLLM:
    model = "fake"

    def __init__(self, reply="ok"):
        self.reply = reply
        self.prompts = []

    async def generate(self, messages, **kwargs):
        self.prompts.append("\n".join(m.content for m in messages))
        return LLMResponse(content=self.reply, input_tokens=1, output_tokens=1,
                           model="fake", provider="fake", estimated_cost_usd=0.0)

    def get_model_name(self):
        return "fake"

    def get_provider_name(self):
        return "fake"


@pytest.fixture(autouse=True)
def _reset_limits():
    reset_rate_limits()


def _note(db, path="03 Permanent Notes/Quokka.md", title="Quokka"):
    note = Note(path=path, title=title, file_hash="h", folder="03 Permanent Notes", tags="[]")
    db.add(note)
    db.commit()
    return note


class TestGrounding:
    async def test_chunk_text_reaches_model_prompt(self, db_session):
        note = _note(db_session)
        db_session.add_all([
            EmbeddingChunk(note_id=note.id, chunk_index=0, content="Intro filler text.", file_hash="h"),
            EmbeddingChunk(note_id=note.id, chunk_index=1,
                           content="The zebrafish protocol uses 42 millilitres of buffer.", file_hash="h"),
        ])
        db_session.commit()
        llm = FakeLLM()
        result = await MentorChatWorkflow(db_session, llm).execute(
            {"message": "Quokka zebrafish protocol", "history": [], "enable_web_search": False}
        )
        assert "42 millilitres of buffer" in llm.prompts[0]
        assert result["source_notes"] == [note.path]

    async def test_semantic_only_scores_not_filtered_out(self, db_session):
        # Blended semantic-only scores are ~0.3-0.5; they must still reach the model.
        from app.services.search.hybrid_search import HybridSearchService
        note = _note(db_session)
        db_session.add(EmbeddingChunk(note_id=note.id, chunk_index=0, content="body", file_hash="h"))
        db_session.commit()
        llm = FakeLLM()
        wf = MentorChatWorkflow(db_session, llm)
        wf.search_svc.search = lambda **kw: [
            {"id": note.id, "path": note.path, "title": note.title, "score": 0.4}
        ]
        result = await wf.execute({"message": "anything", "history": [], "enable_web_search": False})
        assert result["source_notes"] == [note.path]

    async def test_no_cross_session_cache(self, db_session):
        note = _note(db_session)
        db_session.add(EmbeddingChunk(note_id=note.id, chunk_index=0, content="Quokka facts", file_hash="h"))
        db_session.commit()
        llm = FakeLLM()
        wf = MentorChatWorkflow(db_session, llm)
        ctx = {"message": "Quokka", "history": [], "enable_web_search": False}
        await wf.execute(ctx)
        second = await wf.execute(ctx)
        assert len(llm.prompts) == 2
        assert second["cached"] is False


class TestEmbeddingSafety:
    async def test_failed_embedding_keeps_old_chunks(self, db_session):
        note = _note(db_session)
        provider = FakeEmbeddingProvider()
        svc = EmbeddingService(db_session, provider)
        await svc.generate_embeddings_for_note(note, "original body text")
        before = db_session.query(EmbeddingChunk).filter_by(note_id=note.id).count()
        assert before > 0

        async def boom(texts):
            raise RuntimeError("provider down")
        provider.generate_embeddings = boom
        with pytest.raises(RuntimeError):
            await svc.generate_embeddings_for_note(note, "changed body text")
        chunks = db_session.query(EmbeddingChunk).filter_by(note_id=note.id).all()
        assert len(chunks) == before
        assert "original" in chunks[0].content


class TestQuizJudgeFailure:
    async def test_malformed_judge_raises_instead_of_zero(self, db_session):
        wf = QuizScoringWorkflow(db_session, FakeLLM(reply="not json"))
        with pytest.raises(JudgeScoringError):
            await wf.execute({"question": "q", "reference_answer": "a", "one_liner": None,
                              "user_answer": "x", "hints_given": []})

    async def test_out_of_range_score_rejected(self, db_session):
        wf = QuizScoringWorkflow(db_session, FakeLLM(reply='{"score": 250, "feedback": "x"}'))
        with pytest.raises(JudgeScoringError):
            await wf.execute({"question": "q", "reference_answer": "a", "one_liner": None,
                              "user_answer": "x", "hints_given": []})


class TestRateLimit:
    def test_blocks_after_limit(self):
        from fastapi import HTTPException
        for _ in range(3):
            check_rate_limit("k", 3, 60)
        with pytest.raises(HTTPException) as exc:
            check_rate_limit("k", 3, 60)
        assert exc.value.status_code == 429
        check_rate_limit("other", 3, 60)

    def test_chat_over_limit_rejected_before_provider_call(self, client, auth, monkeypatch):
        monkeypatch.setattr(settings, "rate_limit_per_minute", 0)
        r = client.post(f"{API}/chat", headers=auth["headers"],
                        json={"message": "hi", "llm_config": {"provider": "anthropic", "api_key": "k"}})
        assert r.status_code == 429
        assert "Retry-After" in r.headers

    def test_daily_server_cap_applies_only_to_server_key(self, client, auth, monkeypatch):
        monkeypatch.setattr(settings, "daily_server_chat_limit_user", 0)
        monkeypatch.setattr(settings, "llm_api_key", "server-key")
        assert client.post(f"{API}/chat", headers=auth["headers"], json={"message": "hi"}).status_code == 429


class TestHealthStatus:
    def test_unhealthy_returns_503(self, client, monkeypatch):
        from app.utils.monitoring import MonitoringService
        monkeypatch.setattr(MonitoringService, "_check_database", lambda self: False)
        r = client.get(f"{API}/health")
        assert r.status_code == 503
        assert r.json()["status"] == "unhealthy"

    def test_healthy_returns_200(self, client):
        assert client.get(f"{API}/health").status_code == 200


class TestClaudeProviderAsync:
    def test_uses_async_client(self):
        import anthropic
        from app.services.llm.claude_provider import ClaudeProvider
        assert isinstance(ClaudeProvider(api_key="k").client, anthropic.AsyncAnthropic)
