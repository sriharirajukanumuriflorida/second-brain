"""
Integration tests for the read-only shared-access flow:
generate -> claim (browser bind) -> read allowed / writes still blocked,
plus rejection of double-claim, revoked, and expired tokens.
"""
import json
from datetime import datetime, timezone, timedelta

from app.models import Note, AccessToken
from app.services.auth.access_service import AccessTokenService

API = "/api/v1"


def _seed_note(db):
    db.add(Note(
        path="03 Permanent Notes/RAG.md", title="RAG Note", file_hash="h",
        folder="03 Permanent Notes", tags=json.dumps([]), is_archived=False,
    ))
    db.commit()


class TestClaimAndRead:
    def test_read_blocked_without_access(self, client):
        # No login, no cookie -> read endpoint rejects.
        assert client.get(f"{API}/notes").status_code == 401

    def test_claim_then_read(self, client, db_session):
        _seed_note(db_session)
        token = AccessTokenService(db_session).generate().token

        # Claim sets the HTTP-only cookie on the client's cookie jar.
        r = client.post(f"{API}/access/claim", json={"token": token})
        assert r.status_code == 200
        assert r.json()["role"] == "readonly"

        # Now reads work (cookie carried by TestClient automatically).
        notes = client.get(f"{API}/notes")
        assert notes.status_code == 200
        assert any(n["title"] == "RAG Note" for n in notes.json())

        # Dashboards (metrics) also allowed under chosen scope.
        assert client.get(f"{API}/metrics").status_code == 200

    def test_access_status_reports_readonly(self, client, db_session):
        token = AccessTokenService(db_session).generate().token
        client.post(f"{API}/access/claim", json={"token": token})
        r = client.get(f"{API}/access/status")
        assert r.json() == {"kind": "access", "role": "readonly"}


class TestWritesBlocked:
    def test_readonly_cannot_reach_write_endpoints(self, client, db_session):
        """Access visitors have no bearer session, so get_current_user-guarded
        write routes reject them (401/403), never 200."""
        token = AccessTokenService(db_session).generate().token
        client.post(f"{API}/access/claim", json={"token": token})

        # logout requires a real user session -> must be rejected for a visitor.
        r = client.post(f"{API}/auth/logout")
        assert r.status_code in (401, 403)


class TestTokenRejections:
    def test_double_claim_rejected(self, client, db_session):
        token = AccessTokenService(db_session).generate().token
        assert client.post(f"{API}/access/claim", json={"token": token}).status_code == 200
        # Second claim of the same link fails (single-use).
        assert client.post(f"{API}/access/claim", json={"token": token}).status_code == 400

    def test_unknown_token_rejected(self, client):
        assert client.post(f"{API}/access/claim", json={"token": "nope"}).status_code == 400

    def test_revoked_token_rejected(self, client, db_session):
        svc = AccessTokenService(db_session)
        token = svc.generate().token
        svc.revoke(token)
        assert client.post(f"{API}/access/claim", json={"token": token}).status_code == 400

    def test_expired_binding_rejected(self, client, db_session):
        """A claimed-but-expired cookie must not grant access."""
        svc = AccessTokenService(db_session)
        token = svc.generate().token
        binding = svc.claim(token)
        # Force expiry into the past.
        row = db_session.query(AccessToken).filter(AccessToken.token == token).first()
        row.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        db_session.commit()

        client.cookies.set("fde_access", binding)
        assert client.get(f"{API}/notes").status_code == 401
