"""
Authentication utilities and middleware.
"""
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth.session_service import SessionService
from app.services.auth.access_service import AccessTokenService
from app.models import User

security = HTTPBearer()

# Name of the HTTP-only cookie holding a claimed read-only access binding.
ACCESS_COOKIE_NAME = "fde_access"


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    session_service = SessionService(db)
    user = session_service.get_user_by_session(credentials.credentials)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required"
        )
    return current_user


class Principal:
    """Whoever is making the request: a logged-in user OR a read-only visitor.

    `kind` is "user" or "access". `role` is "admin"/"user"/"readonly". Read
    endpoints depend on require_read_access; write endpoints depend on
    get_current_user (which access visitors can't satisfy), so a readonly
    visitor is structurally unable to reach writes.
    """
    def __init__(self, kind: str, role: str, user: User = None):
        self.kind = kind
        self.role = role
        self.user = user


def require_read_access(
    request: Request,
    db: Session = Depends(get_db),
) -> Principal:
    """Allow access to a logged-in user OR a valid read-only access cookie.

    Checks a bearer session first (owner/admin), then falls back to the
    shared-link token (cookie or Authorization bearer). Raises 401 if neither.
    """
    # 1. Bearer session (owner logging in normally)
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[len("Bearer "):]
        user = SessionService(db).get_user_by_session(token)
        if user and user.is_active:
            return Principal("user", user.role, user)

        access = AccessTokenService(db).validate_token(token)
        if access:
            return Principal("access", access.role)

    # 2. Read-only access cookie (shared link visitor)
    binding = request.cookies.get(ACCESS_COOKIE_NAME)
    access = AccessTokenService(db).validate_binding(binding) if binding else None
    if access:
        return Principal("access", access.role)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Read access requires login or a valid access link",
    )
