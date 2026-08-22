"""
Read-only shared-access endpoints.

A visitor opens a share link (…/access?token=XYZ); the frontend posts that token
to /access/claim, which binds it to their browser via an HTTP-only cookie and
starts the 24h clock. Subsequent requests are authorized by require_read_access.
"""
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.config import settings
from app.services.auth.access_service import AccessTokenService
from app.utils.auth import require_read_access, Principal, ACCESS_COOKIE_NAME

router = APIRouter()


class ClaimRequest(BaseModel):
    token: str


@router.post("/access/claim")
async def claim_access(payload: ClaimRequest, response: Response, db: Session = Depends(get_db)):
    """Claim a share link and bind read-only access to this browser."""
    service = AccessTokenService(db)
    binding = service.claim(payload.token)
    if binding is None:
        raise HTTPException(
            status_code=400,
            detail="Link is invalid, already used, expired, or revoked.",
        )

    # HTTP-only so JS can't read it; SameSite=Lax; Secure in production.
    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=binding,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=24 * 60 * 60,
    )
    return {"status": "claimed", "role": "readonly"}


@router.get("/access/status")
async def access_status(principal: Principal = Depends(require_read_access)):
    """Report how the caller is authorized (login vs. read-only link)."""
    return {"kind": principal.kind, "role": principal.role}


@router.post("/access/logout")
async def access_logout(response: Response):
    """Clear the read-only access cookie in this browser."""
    response.delete_cookie(ACCESS_COOKIE_NAME)
    return {"status": "cleared"}
