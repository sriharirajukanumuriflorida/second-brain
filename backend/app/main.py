"""
FastAPI application main entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.database import init_db
from app.api import health, sync, status, notes, folders, search, workflows, github, embeddings, auth, monitoring, access, chat
from app.utils.security import limiter

# Create FastAPI app
app = FastAPI(
    title="FDE Vault Agent Platform",
    description="Backend for FDE Vault Agent Platform - Phase 8: Deployment and Operations",
    version="0.7.0"
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
# Explicit origins (not "*") because allow_credentials=True; the combination of
# "*" + credentials is invalid per the CORS spec and browsers reject it.
# Origins are driven by config so prod (Vercel URL) and local differ via env.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(sync.router, prefix=settings.api_prefix, tags=["Sync"])
app.include_router(status.router, prefix=settings.api_prefix, tags=["Status"])
app.include_router(notes.router, prefix=settings.api_prefix, tags=["Notes"])
app.include_router(folders.router, prefix=settings.api_prefix, tags=["Folders"])
app.include_router(search.router, prefix=settings.api_prefix, tags=["Search"])
app.include_router(workflows.router, prefix=settings.api_prefix, tags=["Workflows"])
app.include_router(github.router, prefix=settings.api_prefix, tags=["GitHub"])
app.include_router(embeddings.router, prefix=settings.api_prefix, tags=["Embeddings"])
app.include_router(auth.router, prefix=settings.api_prefix, tags=["Auth"])
app.include_router(access.router, prefix=settings.api_prefix, tags=["Access"])
app.include_router(monitoring.router, prefix=settings.api_prefix, tags=["Monitoring"])
app.include_router(chat.router, prefix=settings.api_prefix, tags=["Chat"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup, and optionally re-sync the vault.

    Skipped under tests (TESTING=1): the app would otherwise try to connect to
    the real DATABASE_URL on startup, and the test suite provides its own
    in-memory schema via fixtures.

    When AUTO_SYNC_ON_STARTUP is enabled, kick off a vault sync in the
    background (clone + index + embed changed notes). This is for hosts with an
    ephemeral filesystem where the clone is wiped on each restart. It runs
    fire-and-forget so a slow or failing git/network operation never blocks or
    crashes app startup — failures are recorded via the sync event + logs.
    """
    import os
    if os.getenv("TESTING") == "1":
        return
    init_db()

    if settings.auto_sync_on_startup:
        import asyncio
        asyncio.create_task(_auto_sync())


async def _auto_sync():
    """Background vault sync on startup. Never raises into the event loop."""
    from app.database import SessionLocal
    from app.models import SyncEvent
    from app.api.sync import run_sync_task
    from app.utils.logger import log_event

    db = SessionLocal()
    try:
        sync_event = SyncEvent(status="started")
        db.add(sync_event)
        db.commit()
        db.refresh(sync_event)
        # force=True: the ephemeral clone may be gone, so guarantee a fresh one.
        await run_sync_task(db, sync_event.id, force=True)
    except Exception as e:  # pragma: no cover - defensive; boot must not crash
        try:
            log_event(db, "startup.auto_sync_failed", {"error": str(e)})
        except Exception:
            pass
    finally:
        db.close()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "FDE Vault Agent Platform API",
        "version": "0.7.0",
        "phase": "8 - Deployment and Operations",
        "docs": "/docs"
    }
