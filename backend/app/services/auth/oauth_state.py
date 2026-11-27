"""Signed, expiring OAuth state. The browser binding comes from the frontend
keeping the value in sessionStorage and comparing it on return."""
import hashlib
import hmac
import secrets
import time

from app.config import settings

STATE_TTL_SECONDS = 600


def _sign(payload: str) -> str:
    key = settings.github_oauth_client_secret.encode()
    return hmac.new(key, payload.encode(), hashlib.sha256).hexdigest()


def create_state() -> str:
    payload = f"{secrets.token_urlsafe(16)}.{int(time.time()) + STATE_TTL_SECONDS}"
    return f"{payload}.{_sign(payload)}"


def verify_state(state: str) -> bool:
    if not settings.github_oauth_client_secret:
        return False
    try:
        nonce, expiry, sig = state.rsplit(".", 2)
        expires_at = int(expiry)
    except (ValueError, AttributeError):
        return False
    if not hmac.compare_digest(sig, _sign(f"{nonce}.{expiry}")):
        return False
    return expires_at > time.time()
