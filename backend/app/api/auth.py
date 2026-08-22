"""
Authentication API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth.oauth_service import GitHubOAuthService
from app.services.auth.session_service import SessionService
from app.services.auth.user_service import UserService
from app.utils.auth import get_current_user
from app.models import User
from pydantic import BaseModel
from typing import Optional
import secrets

security = HTTPBearer()

router = APIRouter()


class LoginResponse(BaseModel):
    """Login response."""
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    """User response."""
    id: int
    username: str
    email: Optional[str]
    avatar_url: Optional[str]
    role: str


@router.get("/auth/github/login")
async def github_login():
    """Get GitHub OAuth login URL."""
    oauth_service = GitHubOAuthService()
    state = secrets.token_urlsafe(16)
    auth_url = oauth_service.get_authorization_url(state)
    
    return {
        "auth_url": auth_url,
        "state": state
    }


@router.post("/auth/github/callback")
async def github_callback(code: str, state: str, db: Session = Depends(get_db)):
    """Handle GitHub OAuth callback."""
    try:
        oauth_service = GitHubOAuthService()
        
        # Fetch token
        token = oauth_service.fetch_token(code)
        access_token = token.get("access_token")
        
        # Get user info
        user_info = oauth_service.get_user_info(access_token)
        
        # Get or create user
        user_service = UserService(db)
        user = user_service.get_or_create_user(
            github_id=str(user_info.get("id")),
            username=user_info.get("login"),
            email=user_info.get("email"),
            avatar_url=user_info.get("avatar_url")
        )
        
        # Create session
        session_service = SessionService(db)
        session_token = session_service.create_session(user.id)
        
        return LoginResponse(
            access_token=session_token,
            user={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "avatar_url": user.avatar_url,
                "role": user.role
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/auth/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout user by invalidating the current session token server-side."""
    session_service = SessionService(db)
    # The bearer token IS the session token (see SessionService.create_session).
    # Deleting it enforces server-side invalidation so a leaked token stops working.
    session_service.invalidate_session(credentials.credentials)
    return {"message": "Logged out successfully"}


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user info."""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        avatar_url=current_user.avatar_url,
        role=current_user.role
    )
