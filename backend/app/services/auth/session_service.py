"""
Session management service.
"""
from sqlalchemy.orm import Session
from app.models import User, Session as SessionModel
from datetime import datetime, timedelta
import secrets
from typing import Optional


class SessionService:
    """Service for managing user sessions."""

    def __init__(self, db: Session):
        self.db = db

    def create_session(self, user_id: int, expires_hours: int = 24) -> str:
        """Create a new session for a user."""
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=expires_hours)

        session = SessionModel(
            user_id=user_id,
            session_token=session_token,
            expires_at=expires_at
        )

        self.db.add(session)
        self.db.commit()

        return session_token

    def get_user_by_session(self, session_token: str) -> Optional[User]:
        """Get user by session token."""
        session = self.db.query(SessionModel).filter(
            SessionModel.session_token == session_token,
            SessionModel.expires_at > datetime.now()
        ).first()

        if session:
            return session.user
        return None

    def invalidate_session(self, session_token: str) -> bool:
        """Invalidate a session."""
        session = self.db.query(SessionModel).filter(
            SessionModel.session_token == session_token
        ).first()

        if session:
            self.db.delete(session)
            self.db.commit()
            return True
        return False

    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        count = self.db.query(SessionModel).filter(
            SessionModel.expires_at < datetime.now()
        ).delete()
        self.db.commit()
        return count
