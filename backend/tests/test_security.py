"""Security hardening: login allowlist, signed OAuth state, chat session ownership."""
import pytest

from app.config import settings
from app.models import ChatSession, User
from app.services.auth import oauth_state
from app.services.auth.access_service import AccessTokenService
from app.services.auth.session_service import SessionService

API = "/api/v1"


@pytest.fixture(autouse=True)
def oauth_secret(monkeypatch):
    monkeypatch.setattr(settings, "github_oauth_client_secret", "test-secret")


def _make_user(db, github_id, role="user"):
    user = User(github_id=github_id, username=f"u{github_id}", role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    token = SessionService(db).create_session(user.id)
    return user, {"Authorization": f"Bearer {token}"}


class TestOAuthState:
    def test_roundtrip(self):
        assert oauth_state.verify_state(oauth_state.create_state())

    def test_tampered_rejected(self):
        state = oauth_state.create_state()
        assert not oauth_state.verify_state("x" + state)
        assert not oauth_state.verify_state(state[:-1] + ("0" if state[-1] != "0" else "1"))

    def test_expired_rejected(self, monkeypatch):
        state = oauth_state.create_state()
        monkeypatch.setattr(oauth_state.time, "time", lambda: 4_000_000_000)
        assert not oauth_state.verify_state(state)

    def test_garbage_rejected(self):
        assert not oauth_state.verify_state("nonsense")
        assert not oauth_state.verify_state("")


class TestCallback:
    def _patch_github(self, monkeypatch, gh_id):
        from app.services.auth.oauth_service import GitHubOAuthService
        monkeypatch.setattr(GitHubOAuthService, "fetch_token", lambda self, code: {"access_token": "t"})
        monkeypatch.setattr(
            GitHubOAuthService, "get_user_info",
            lambda self, tok: {"id": gh_id, "login": "someone", "email": None, "avatar_url": None},
        )

    def _callback(self, client, state=None):
        return client.post(
            f"{API}/auth/github/callback",
            params={"code": "c", "state": state or oauth_state.create_state()},
        )

    def test_bad_state_rejected(self, client):
        assert self._callback(client, state="forged").status_code == 400

    def test_unapproved_account_rejected_and_not_created(self, client, db_session, monkeypatch):
        monkeypatch.setattr(settings, "allowed_github_ids", "111")
        self._patch_github(monkeypatch, 999)
        assert self._callback(client).status_code == 403
        assert db_session.query(User).filter(User.github_id == "999").count() == 0

    def test_empty_allowlist_fails_closed(self, client, monkeypatch):
        monkeypatch.setattr(settings, "allowed_github_ids", "")
        self._patch_github(monkeypatch, 111)
        assert self._callback(client).status_code == 403

    def test_allowlisted_account_logs_in(self, client, monkeypatch):
        monkeypatch.setattr(settings, "allowed_github_ids", "111, 222")
        self._patch_github(monkeypatch, 222)
        r = self._callback(client)
        assert r.status_code == 200
        assert r.json()["access_token"]

    def test_existing_admin_not_locked_out(self, client, db_session, monkeypatch):
        monkeypatch.setattr(settings, "allowed_github_ids", "")
        _make_user(db_session, "555", role="admin")
        self._patch_github(monkeypatch, 555)
        assert self._callback(client).status_code == 200


class TestUnapprovedSessions:
    def test_unapproved_existing_user_blocked_everywhere(self, client, db_session, monkeypatch):
        monkeypatch.setattr(settings, "allowed_github_ids", "")
        _, headers = _make_user(db_session, "777")
        assert client.get(f"{API}/auth/me", headers=headers).status_code == 403
        assert client.get(f"{API}/notes", headers=headers).status_code == 401

    def test_allowlisted_user_allowed(self, client, db_session, monkeypatch):
        monkeypatch.setattr(settings, "allowed_github_ids", "777")
        _, headers = _make_user(db_session, "777")
        assert client.get(f"{API}/auth/me", headers=headers).status_code == 200
        assert client.get(f"{API}/notes", headers=headers).status_code == 200


class TestChatSessionOwnership:
    CHAT = {
        "message": "hi",
        "llm_config": {"provider": "anthropic", "api_key": "sk-test"},
    }

    @pytest.fixture
    def two_users(self, db_session, monkeypatch):
        monkeypatch.setattr(settings, "allowed_github_ids", "1,2")
        a, ha = _make_user(db_session, "1")
        b, hb = _make_user(db_session, "2")
        db_session.add(ChatSession(id="session-of-b", user_id=b.id))
        db_session.add(ChatSession(id="anon-session", user_id=None))
        db_session.commit()
        return ha, hb

    def test_other_user_cannot_chat_in_session(self, client, two_users):
        ha, _ = two_users
        r = client.post(f"{API}/chat", json={**self.CHAT, "session_id": "session-of-b"}, headers=ha)
        assert r.status_code == 403

    def test_other_user_cannot_read_usage(self, client, two_users):
        ha, hb = two_users
        assert client.get(f"{API}/chat/usage/session-of-b", headers=ha).status_code == 403
        assert client.get(f"{API}/chat/usage/session-of-b", headers=hb).status_code == 200

    def test_user_cannot_adopt_anonymous_session(self, client, two_users):
        ha, _ = two_users
        r = client.post(f"{API}/chat", json={**self.CHAT, "session_id": "anon-session"}, headers=ha)
        assert r.status_code == 403
        assert client.get(f"{API}/chat/usage/anon-session", headers=ha).status_code == 403

    def test_visitor_cannot_touch_user_session(self, client, db_session, two_users):
        token = AccessTokenService(db_session).generate().token
        assert client.post(f"{API}/access/claim", json={"token": token}).status_code == 200
        r = client.post(f"{API}/chat", json={**self.CHAT, "session_id": "session-of-b"})
        assert r.status_code == 403
        assert client.get(f"{API}/chat/usage/session-of-b").status_code == 403
