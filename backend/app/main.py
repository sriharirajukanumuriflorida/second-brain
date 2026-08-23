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
    """Initialize database on startup.

    Skipped under tests (TESTING=1): the app would otherwise try to connect to
    the real DATABASE_URL on startup, and the test suite provides its own
    in-memory schema via fixtures.
    """
    import os
    if os.getenv("TESTING") == "1":
        return
    init_db()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "FDE Vault Agent Platform API",
        "version": "0.7.0",
        "phase": "8 - Deployment and Operations",
        "docs": "/docs"
    }
