"""
User management service.
"""
from sqlalchemy.orm import Session
from app.models import User
from typing import Optional
from datetime import datetime


class UserService:
    """Service for managing users."""

    def __init__(self, db: Session):
        self.db = db

    def get_or_create_user(self, github_id: str, username: str, email: str, avatar_url: str) -> User:
        """Get existing user or create new one."""
        user = self.db.query(User).filter(User.github_id == github_id).first()

        if user:
            # Update last login
            user.last_login_at = datetime.now()
            self.db.commit()
            return user

        # Create new user
        user = User(
            github_id=github_id,
            username=username,
            email=email,
            avatar_url=avatar_url,
            role="user"  # Default role
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def set_admin_role(self, user_id: int) -> bool:
        """Set user role to admin."""
        user = self.get_user_by_id(user_id)
        if user:
            user.role = "admin"
            self.db.commit()
            return True
        return False

    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin."""
        user = self.get_user_by_id(user_id)
        return user and user.role == "admin"
