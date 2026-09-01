"""
Embedding generation service.
"""
from typing import List, Dict, Any
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.models import Note, EmbeddingChunk
from app.services.embeddings.base import BaseEmbeddingProvider
from app.services.chunking.chunker import MarkdownChunker
from app.services.hash_service import calculate_content_hash
from app.utils.logger import log_event
from datetime import datetime, timezone
import json


class EmbeddingService:
    """Service for generating and managing embeddings."""

    def __init__(self, db: Session, embedding_provider: BaseEmbeddingProvider):
        self.db = db
        self.embedding_provider = embedding_provider
        self.chunker = MarkdownChunker(
            chunk_size=750,
            overlap=100,
            max_tokens=1000,
            min_tokens=500
        )

    async def generate_embeddings_for_note(
        self,
        note: Note,
        content: str,
        replace_existing: bool = True
    ) -> Dict[str, Any]:
        """Generate embeddings for a note.

        When ``replace_existing`` is True (the default, used by the sync flow),
        the note's existing chunks are deleted first. Re-chunking changed
        content shifts chunk boundaries and hashes, so without this the old
        chunks would linger as orphans and pollute semantic search results.
        """
        try:
            log_event(self.db, "embedding.started", {"note_id": note.id, "path": note.path})

            if replace_existing:
                deleted = self.db.query(EmbeddingChunk).filter(
                    EmbeddingChunk.note_id == note.id
                ).delete()
                if deleted:
                    self.db.commit()

            # Prepare metadata
            metadata = {
                "note_id": note.id,
                "path": note.path,
                "title": note.title,
                "tags": note.tags,
                "folder": note.folder
            }

            # Chunk the content
            chunks = self.chunker.chunk_text(content, metadata)

            # Generate embeddings for chunks
            chunk_texts = [chunk["content"] for chunk in chunks]
            embeddings = await self.embedding_provider.generate_embeddings(chunk_texts)

            # Store embeddings
            chunks_created = 0
            chunks_updated = 0
            # Track (EmbeddingChunk, vector) so we can write the pgvector column
            # after commit, once new rows have their DB-assigned ids.
            pending_vectors = []

            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_hash = calculate_content_hash(chunk["content"])

                # Check if chunk already exists
                existing = self.db.query(EmbeddingChunk).filter(
                    EmbeddingChunk.note_id == note.id,
                    EmbeddingChunk.chunk_index == i,
                    EmbeddingChunk.chunk_hash == chunk_hash
                ).first()

                if existing:
                    # Update if stale
                    if existing.is_stale:
                        existing.embedding = self._serialize_embedding(embedding)
                        existing.embedding_provider = self.embedding_provider.get_provider_name()
                        existing.embedding_model = self.embedding_provider.get_model_name()
                        existing.embedded_at = datetime.now(timezone.utc)
                        existing.is_stale = False
                        chunks_updated += 1
                        pending_vectors.append((existing, embedding))
                else:
                    # Create new chunk
                    embedding_chunk = EmbeddingChunk(
                        note_id=note.id,
                        chunk_index=i,
                        content=chunk["content"],
                        heading=chunk["metadata"].get("heading", ""),
                        embedding=self._serialize_embedding(embedding),
                        embedding_provider=self.embedding_provider.get_provider_name(),
                        embedding_model=self.embedding_provider.get_model_name(),
                        embedding_model_version="1.0",
                        embedding_dimensions=self.embedding_provider.get_embedding_dimension(),
                        chunk_hash=chunk_hash,
                        file_hash=note.file_hash,
                        is_stale=False
                    )
                    self.db.add(embedding_chunk)
                    chunks_created += 1
                    pending_vectors.append((embedding_chunk, embedding))

            self.db.commit()

            # Populate the real pgvector column now that rows have ids (Postgres only).
            for chunk_row, embedding in pending_vectors:
                self._write_pgvector(chunk_row.id, embedding)
            if pending_vectors:
                self.db.commit()

            log_event(self.db, "embedding.completed", {
                "note_id": note.id,
                "chunks_created": chunks_created,
                "chunks_updated": chunks_updated
            })

            return {
                "chunks_created": chunks_created,
                "chunks_updated": chunks_updated,
                "total_chunks": len(chunks)
            }

        except Exception as e:
            log_event(self.db, "embedding.failed", {"note_id": note.id, "error": str(e)})
            raise

    def _serialize_embedding(self, embedding: List[float]) -> bytes:
        """Serialize embedding to bytes (legacy blob storage)."""
        import struct
        return struct.pack(f"{len(embedding)}f", *embedding)

    def _write_pgvector(self, chunk_id: int, embedding: List[float]) -> None:
        """Write the embedding into the real pgvector column (embedding_vec).

        The ORM model has no pgvector type, and the column is created by
        supabase/bootstrap.sql, so we set it with raw SQL. Cast a Postgres
        array literal to vector. No-ops silently on SQLite / when the column
        is absent, so local keyword-only runs are unaffected.
        """
        if "postgresql" not in str(self.db.bind.url) and "postgres" not in str(self.db.bind.url):
            return
        try:
            vec_literal = "[" + ",".join(repr(float(x)) for x in embedding) + "]"
            self.db.execute(
                text("UPDATE embedding_chunks SET embedding_vec = :vec WHERE id = :id"),
                {"vec": vec_literal, "id": chunk_id},
            )
        except Exception as e:  # pragma: no cover - column may not exist yet
            log_event(self.db, "embedding.pgvector_write_failed", {"chunk_id": chunk_id, "error": str(e)})

    def mark_embeddings_stale(self, model: str) -> int:
        """Mark embeddings as stale when model changes."""
        count = self.db.query(EmbeddingChunk).filter(
            EmbeddingChunk.embedding_model != model
        ).update({"is_stale": True})
        self.db.commit()
        return count

    async def re_embed_stale_chunks(self, limit: int = 100) -> Dict[str, int]:
        """Re-embed stale chunks."""
        stale_chunks = self.db.query(EmbeddingChunk).filter(
            EmbeddingChunk.is_stale == True
        ).limit(limit).all()

        re_embedded = 0

        for chunk in stale_chunks:
            # Generate new embedding
            embeddings = await self.embedding_provider.generate_embeddings([chunk.content])
            chunk.embedding = self._serialize_embedding(embeddings[0])
            chunk.embedding_provider = self.embedding_provider.get_provider_name()
            chunk.embedding_model = self.embedding_provider.get_model_name()
            chunk.embedded_at = datetime.now(timezone.utc)
            chunk.is_stale = False
            re_embedded += 1

        self.db.commit()

        return {"re_embedded": re_embedded}
