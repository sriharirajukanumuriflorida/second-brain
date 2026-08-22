"""
Security utilities for rate limiting and CORS configuration.
"""
from fastapi import Request, HTTPException, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import Callable
import secrets

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


def get_api_key(request: Request) -> str:
    """Get API key from request header."""
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    return api_key


def validate_cors_origin(origin: str, allowed_origins: list) -> bool:
    """Validate CORS origin."""
    if origin in allowed_origins:
        return True
    return False


def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token."""
    return secrets.token_urlsafe(length)
