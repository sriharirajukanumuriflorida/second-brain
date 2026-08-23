"""
Read-only shared-access endpoints.

A visitor opens a share link (…/access?token=XYZ); the frontend posts that token
to /access/claim, which binds it to their browser via an HTTP-only cookie and
starts the 24h clock. Subsequent requests are authorized by require_read_access.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.config import settings
from app.models import User
from app.schemas import GenerateAccessLinkRequest, GenerateAccessLinkResponse, AccessLinkResponse
from app.services.auth.access_service import AccessTokenService
from app.utils.auth import require_read_access, require_admin, Principal, ACCESS_COOKIE_NAME

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


@router.post("/access/generate", response_model=GenerateAccessLinkResponse)
async def generate_access_link(
    payload: GenerateAccessLinkRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Mint a new read-only share token (admin only)."""
    service = AccessTokenService(db)
    token = service.generate(ttl_hours=payload.hours, label=payload.label, role="readonly")
    return GenerateAccessLinkResponse(
        id=token.id,
        token=token.token,
        label=token.label,
        ttl_hours=token.ttl_hours,
        created_at=token.created_at,
    )


@router.get("/access/list", response_model=List[AccessLinkResponse])
async def list_access_links(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """List all share links, newest first (admin only)."""
    service = AccessTokenService(db)
    return [
        AccessLinkResponse(
            id=row.id,
            label=row.label,
            role=row.role,
            ttl_hours=row.ttl_hours,
            created_at=row.created_at,
            claimed_at=row.claimed_at,
            expires_at=row.expires_at,
            revoked=row.revoked,
            is_claimed=row.browser_binding is not None,
        )
        for row in service.list_all()
    ]


@router.post("/access/{token_id}/revoke")
async def revoke_access_link(
    token_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Revoke a share link by id, killing any active access immediately (admin only)."""
    service = AccessTokenService(db)
    if not service.revoke_by_id(token_id):
        raise HTTPException(status_code=404, detail="Access link not found")
    return {"status": "revoked"}
