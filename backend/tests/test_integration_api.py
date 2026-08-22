"""
Integration tests hitting the FastAPI app through TestClient with an
in-memory DB. Covers health, auth protection, logout invalidation, and search.
"""
import json
from app.models import Note

API = "/api/v1"


class TestHealth:
    def test_health_ok(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"

    def test_root(self, client):
        assert client.get("/").status_code == 200


class TestAuthProtection:
    def test_me_requires_auth(self, client):
        # No bearer token -> HTTPBearer rejects with 403 (no credentials).
        assert client.get(f"{API}/auth/me").status_code == 403

    def test_me_rejects_bad_token(self, client):
        r = client.get(f"{API}/auth/me", headers={"Authorization": "Bearer nope"})
        assert r.status_code == 401

    def test_me_with_valid_session(self, client, auth):
        r = client.get(f"{API}/auth/me", headers=auth["headers"])
        assert r.status_code == 200
        assert r.json()["username"] == "tester"


class TestLogoutInvalidation:
    def test_logout_invalidates_token(self, client, auth):
        # token works before logout
        assert client.get(f"{API}/auth/me", headers=auth["headers"]).status_code == 200
        # logout
        assert client.post(f"{API}/auth/logout", headers=auth["headers"]).status_code == 200
        # same token is now rejected -> proves server-side invalidation
        assert client.get(f"{API}/auth/me", headers=auth["headers"]).status_code == 401


class TestSearchEndpoint:
    def test_search_returns_keyword_hits(self, client, db_session, auth):
        note = Note(
            path="03 Permanent Notes/RAG Evaluation Metrics.md",
            title="RAG Evaluation Metrics",
            file_hash="h",
            folder="03 Permanent Notes",
            tags=json.dumps([]),
            is_archived=False,
        )
        db_session.add(note)
        db_session.commit()

        # /search now requires read access; use the logged-in owner's bearer.
        # semantic=false forces keyword-only (no embedding key needed).
        r = client.get(
            f"{API}/search",
            params={"query": "RAG", "semantic": "false"},
            headers=auth["headers"],
        )
        assert r.status_code == 200
        titles = [item["title"] for item in r.json()]
        assert "RAG Evaluation Metrics" in titles
