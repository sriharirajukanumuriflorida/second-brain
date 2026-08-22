"""
Database connection and schema management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create database engine
def _build_connect_args() -> dict:
    """Driver-specific connection args.

    SQLite needs check_same_thread=False. On Postgres we target Supabase's
    transaction pooler (PgBouncer, port 6543), which does NOT support named
    prepared statements — psycopg2 uses server-side prepared statements only
    for executemany, so we disable statement caching to be safe and keep
    keepalives on so idle pooled connections aren't silently dropped.
    """
    if "sqlite" in settings.database_url:
        return {"check_same_thread": False}
    if settings.database_url.startswith(("postgresql", "postgres")):
        return {
            # Supabase requires SSL. psycopg2 does not request it by default,
            # which makes the pooler accept the TCP connection then close it
            # ("server closed the connection unexpectedly"). Force it here so it
            # works the same locally and on Render, regardless of the URL.
            "sslmode": "require",
            # Recycle connections so a keepalive'd-but-stale pooled conn is replaced
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5,
        }
    return {}


engine = create_engine(
    settings.database_url,
    connect_args=_build_connect_args(),
    # PgBouncer transaction mode shares connections across requests; a bounded
    # pool that recycles avoids exhausting the pooler and dropped-connection errors.
    pool_pre_ping=True,
    pool_recycle=280,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
