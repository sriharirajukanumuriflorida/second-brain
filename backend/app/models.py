"""
SQLAlchemy models for vault metadata.
"""
from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Note(Base):
    """Note metadata model."""

    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    file_hash = Column(String, index=True, nullable=False)
    content_hash = Column(String, nullable=True)
    frontmatter_hash = Column(String, nullable=True)
    tags = Column(Text, nullable=True)  # JSON array as string
    backlinks = Column(Text, nullable=True)  # JSON array as string
    frontmatter = Column(Text, nullable=True)  # YAML as string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_indexed_at = Column(DateTime(timezone=True), server_default=func.now())
    is_archived = Column(Boolean, default=False)
    folder = Column(String, index=True, nullable=False)


class SyncEvent(Base):
    """Sync event tracking model."""

    __tablename__ = "sync_events"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, nullable=False)  # started, completed, failed
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    notes_processed = Column(Integer, default=0)
    notes_indexed = Column(Integer, default=0)
    notes_updated = Column(Integer, default=0)


class AuditLog(Base):
    """Audit log model."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, index=True, nullable=False)
    event_data = Column(Text, nullable=True)  # JSON as string
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class EmbeddingChunk(Base):
    """Embedding chunk model for semantic search."""

    __tablename__ = "embedding_chunks"

    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, index=True, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    heading = Column(String, nullable=True)
    embedding = Column(LargeBinary, nullable=True)  # pgvector as binary
    embedding_provider = Column(String, nullable=True)
    embedding_model = Column(String, nullable=True)
    embedding_model_version = Column(String, nullable=True)
    embedding_dimensions = Column(Integer, nullable=True)
    chunk_hash = Column(String, index=True, nullable=True)
    file_hash = Column(String, index=True, nullable=False)
    embedded_at = Column(DateTime(timezone=True), server_default=func.now())
    is_stale = Column(Boolean, default=False)


class User(Base):
    """User model for authentication."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    role = Column(String, default="user")  # admin or user
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)


class Session(Base):
    """User session model."""

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="sessions")


class ChatSession(Base):
    """A multi-turn chat session."""

    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, index=True)  # UUID set by caller
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # null for shared-link visitors
    summary = Column(Text, nullable=True)  # compressed history for old turns
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """A single message in a chat session."""

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    source_notes = Column(Text, nullable=True)   # JSON list of note paths
    web_sources = Column(Text, nullable=True)    # JSON list of {title, url, snippet}
    model = Column(String, nullable=True)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ChatSession", back_populates="messages")


class ChatCache(Base):
    """1-hour reply cache keyed on query + top-note hash."""

    __tablename__ = "chat_cache"

    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String, unique=True, index=True, nullable=False)
    reply = Column(Text, nullable=False)
    source_notes = Column(Text, nullable=True)   # JSON
    web_sources = Column(Text, nullable=True)    # JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)


class AccessToken(Base):
    """One-time, browser-bound, time-limited read-only access grant.

    Lifecycle: generated (unclaimed) -> claimed (bound to a browser, 24h clock
    starts) -> expired/revoked. Lets the owner share read-only access via a link
    without the recipient needing a GitHub account. See app/api/access.py.
    """

    __tablename__ = "access_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    # Set at claim time — the random value stored in the visitor's HTTP-only
    # cookie. Presence means the link has been claimed and is bound to a browser.
    browser_binding = Column(String, unique=True, index=True, nullable=True)
    role = Column(String, default="readonly", nullable=False)
    label = Column(String, nullable=True)  # optional note, e.g. who it was for
    ttl_hours = Column(Integer, default=24, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    claimed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # set at claim
    revoked = Column(Boolean, default=False, nullable=False)
