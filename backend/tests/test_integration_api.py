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


class TestStatusEndpoint:
    def test_status_returns_ok(self, client, auth):
        # Regression test: vault_path is a pathlib.Path in settings but
        # StatusResponse.vault_path is typed str — passing the Path object
        # directly used to fail FastAPI's response validation with a 500.
        r = client.get(f"{API}/status", headers=auth["headers"])
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body["vault_path"], str)
        assert isinstance(body["total_notes"], int)


class TestAuthZGatekeeping:
    def test_status_requires_read_access(self, client):
        assert client.get(f"{API}/status").status_code == 401

    def test_sync_requires_login(self, client):
        assert client.post(f"{API}/sync", json={"force": False}).status_code == 403

    def test_workflows_requires_login(self, client):
        r = client.post(
            f"{API}/workflows",
            json={"workflow_type": "solution_brief", "content": "x"},
        )
        assert r.status_code == 403

    def test_embeddings_requires_login(self, client):
        assert client.post(f"{API}/embeddings/generate", json={"note_id": 1}).status_code == 403

    def test_github_workflow_requires_login(self, client):
        r = client.post(
            f"{API}/github/workflow",
            json={"workflow_type": "solution_brief", "content": "x", "title": "x"},
        )
        assert r.status_code == 403


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


class TestVaultOnlyFiltering:
    def test_notes_folders_and_search_skip_repo_docs(self, client, db_session, auth):
        db_session.add_all([
            Note(
                path="backend/README.md",
                title="Backend README",
                file_hash="a",
                folder="backend",
                tags=json.dumps([]),
                is_archived=False,
            ),
            Note(
                path="frontend/README.md",
                title="Frontend README",
                file_hash="b",
                folder="frontend",
                tags=json.dumps([]),
                is_archived=False,
            ),
            Note(
                path="03 Permanent Notes/Real Note.md",
                title="Real Note",
                file_hash="c",
                folder="03 Permanent Notes",
                tags=json.dumps([]),
                is_archived=False,
            ),
        ])
        db_session.commit()

        notes = client.get(f"{API}/notes", headers=auth["headers"]).json()
        assert [n["title"] for n in notes] == ["Real Note"]

        folders = client.get(f"{API}/folders", headers=auth["headers"]).json()
        assert [f["name"] for f in folders] == ["03 Permanent Notes"]

        search = client.get(
            f"{API}/search",
            params={"query": "Note", "semantic": "false"},
            headers=auth["headers"],
        ).json()
        assert [r["title"] for r in search] == ["Real Note"]
