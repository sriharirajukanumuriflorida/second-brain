"""In-process sliding-window rate limits keyed by principal (not IP, which is
shared behind Render's proxy). Single-instance only: counters are not shared
across processes."""
import time
from collections import defaultdict, deque

from fastapi import HTTPException

_hits: dict[str, deque] = defaultdict(deque)


def check_rate_limit(key: str, limit: int, window_seconds: int) -> None:
    """Record a hit for `key`; raise 429 if it exceeds `limit` in the window."""
    now = time.monotonic()
    hits = _hits[key]
    while hits and now - hits[0] > window_seconds:
        hits.popleft()
    if len(hits) >= limit:
        retry_after = max(1, int(window_seconds - (now - hits[0]))) if hits else window_seconds
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please slow down.",
            headers={"Retry-After": str(retry_after)},
        )
    hits.append(now)


def reset_rate_limits() -> None:
    _hits.clear()
