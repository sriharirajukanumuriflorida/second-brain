"""
Unit tests for session lifecycle — underpins the logout fix.
"""
from app.models import User
from app.services.auth.session_service import SessionService


def _make_user(db):
    user = User(github_id="1", username="u", email=None, role="user")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_create_then_resolve_session(db_session):
    user = _make_user(db_session)
    svc = SessionService(db_session)
    token = svc.create_session(user.id)
    assert svc.get_user_by_session(token).id == user.id


def test_invalidate_session_makes_token_unusable(db_session):
    """This is exactly what /auth/logout now relies on."""
    user = _make_user(db_session)
    svc = SessionService(db_session)
    token = svc.create_session(user.id)

    assert svc.invalidate_session(token) is True
    assert svc.get_user_by_session(token) is None


def test_invalidate_unknown_token_returns_false(db_session):
    svc = SessionService(db_session)
    assert svc.invalidate_session("not-a-real-token") is False
