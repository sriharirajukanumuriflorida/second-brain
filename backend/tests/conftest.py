"""
Shared pytest fixtures: in-memory DB, FastAPI test client, and an auth helper.
"""
# Set env BEFORE importing app modules so app.config.settings and the module-level
# engine never bind to the real Supabase DATABASE_URL from .env. Env vars take
# precedence over the .env file in pydantic-settings.
import os
os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = "sqlite://"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.models import User
from app.services.auth.session_service import SessionService


@pytest.fixture
def db_session():
    """A fresh in-memory SQLite DB per test.

    StaticPool + a single shared connection keeps the in-memory schema alive
    across the session and the request-scoped sessions the app opens.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """TestClient wired to the in-memory DB via dependency override."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth(db_session):
    """Create a user + valid session; return (user, token, headers)."""
    user = User(github_id="123", username="tester", email="t@example.com", role="admin")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = SessionService(db_session).create_session(user.id)
    headers = {"Authorization": f"Bearer {token}"}
    return {"user": user, "token": token, "headers": headers}
