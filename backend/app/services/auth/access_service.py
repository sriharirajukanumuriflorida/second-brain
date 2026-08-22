"""
Read-only access-token service.

Implements one-time, browser-bound, time-limited (default 24h) read-only access
grants so the owner can share the app via a link without the recipient needing a
GitHub account.

Lifecycle:
  generate()  -> creates an unclaimed token (the value that goes in the link)
  claim()     -> first visitor binds it to their browser; 24h clock starts
  validate_binding() -> checks the per-browser cookie value on each request
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
import secrets

from sqlalchemy.orm import Session
from app.models import AccessToken


class AccessTokenService:
    def __init__(self, db: Session):
        self.db = db

    def generate(self, ttl_hours: int = 24, label: Optional[str] = None,
                 role: str = "readonly") -> AccessToken:
        """Create a new unclaimed access token (the link value)."""
        token = AccessToken(
            token=secrets.token_urlsafe(32),
            role=role,
            label=label,
            ttl_hours=ttl_hours,
        )
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token

    def claim(self, token_value: str) -> Optional[str]:
        """Claim a link on first open; bind it to a new browser.

        Returns the browser_binding value to set as an HTTP-only cookie, or None
        if the token is unknown, revoked, already claimed, or expired.
        """
        row = self.db.query(AccessToken).filter(
            AccessToken.token == token_value
        ).first()

        if row is None or row.revoked:
            return None
        # Already claimed -> the link is single-use; reject a second claim.
        if row.browser_binding is not None:
            return None

        now = datetime.now(timezone.utc)
        binding = secrets.token_urlsafe(32)
        row.browser_binding = binding
        row.claimed_at = now
        row.expires_at = now + timedelta(hours=row.ttl_hours)
        self.db.commit()
        return binding

    def validate_binding(self, binding: str) -> Optional[AccessToken]:
        """Return the live AccessToken for a browser cookie, or None if invalid."""
        if not binding:
            return None
        row = self.db.query(AccessToken).filter(
            AccessToken.browser_binding == binding
        ).first()
        if row is None or row.revoked or row.expires_at is None:
            return None
        # Some backends (SQLite) return naive datetimes; normalize to UTC-aware
        # before comparing so tz-naive vs tz-aware never raises.
        expires = row.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires <= datetime.now(timezone.utc):
            return None
        return row

    def revoke(self, token_value: str) -> bool:
        """Revoke a token by its original link value (kills active access)."""
        row = self.db.query(AccessToken).filter(
            AccessToken.token == token_value
        ).first()
        if row is None:
            return False
        row.revoked = True
        self.db.commit()
        return True
