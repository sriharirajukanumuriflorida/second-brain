"""
Hybrid search service (keyword + semantic).
"""
from typing import List, Dict, Any, Optional
from sqlalchemy import text, or_
from sqlalchemy.orm import Session
from app.models import Note, EmbeddingChunk
from app.config import settings

# Cap the filesystem fallback scan so a keyword-only deployment with many
# un-embedded notes never turns a search into an unbounded disk walk.
_FS_SCAN_CAP = 400


class HybridSearchService:
    """Service for hybrid keyword + semantic search."""

    def __init__(self, db: Session):
        self.db = db

    def search(
        self,
        query: str,
        folder: Optional[str] = None,
        limit: int = 20,
        semantic_weight: float = 0.5,
        keyword_weight: float = 0.5,
        query_embedding: Optional[List[float]] = None,
    ) -> List[Dict[str, Any]]:
        """Hybrid search combining keyword and semantic results.

        Keyword search always runs. If a query_embedding is supplied AND
        pgvector semantic search is available, the two result sets are blended
        by weighted score. Otherwise this degrades to keyword-only, so it works
        unchanged on local SQLite where pgvector does not exist.
        """
        keyword_results = self._keyword_search(query, folder, limit)

        if query_embedding is None or not self.semantic_search_available():
            return keyword_results

        semantic_results = self._semantic_search(query_embedding, folder, limit)
        if not semantic_results:
            return keyword_results

        return self._blend(
            keyword_results, semantic_results, keyword_weight, semantic_weight, limit
        )

    def _keyword_search(
        self,
        query: str,
        folder: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Keyword search over note title, frontmatter, and body.

        Body coverage comes from two sources, unioned by note id:
          1. EmbeddingChunk.content — the chunked note body, already in the DB
             once a note is embedded. Pure SQL, no disk access.
          2. Filesystem fallback — for notes with no chunks yet (e.g. keyword-
             only / un-embedded deployments), read the .md from VAULT_PATH and
             substring-match. Bounded by _FS_SCAN_CAP so it can't run away.
        Title/frontmatter matches outrank body-only matches.
        """
        base_filters = [
            Note.is_archived == False,
            or_(*[Note.folder.like(f"{digit}%") for digit in "0123456789"]),
            Note.folder != "14 Agent Outputs",
        ]
        if folder:
            base_filters.append(Note.folder == folder)

        pattern = f"%{query}%"

        # 1) Title / frontmatter matches (strong signal -> score 1.0).
        meta_notes = (
            self.db.query(Note)
            .filter(*base_filters)
            .filter((Note.title.ilike(pattern)) | (Note.frontmatter.ilike(pattern)))
            .limit(limit)
            .all()
        )

        merged: Dict[int, Dict[str, Any]] = {}
        for note in meta_notes:
            merged[note.id] = self._kw_row(note, 1.0)

        # 2) Body matches via embedded chunk content (weaker signal -> 0.7).
        if len(merged) < limit:
            chunk_notes = (
                self.db.query(Note)
                .join(EmbeddingChunk, EmbeddingChunk.note_id == Note.id)
                .filter(*base_filters)
                .filter(EmbeddingChunk.content.ilike(pattern))
                .distinct()
                .limit(limit)
                .all()
            )
            for note in chunk_notes:
                if note.id not in merged:
                    merged[note.id] = self._kw_row(note, 0.7)

        # 3) Filesystem fallback for notes that have no chunks yet.
        if len(merged) < limit:
            self._body_scan_fallback(query, base_filters, merged, limit)

        return sorted(merged.values(), key=lambda r: r["score"], reverse=True)[:limit]

    def _kw_row(self, note: Note, score: float) -> Dict[str, Any]:
        return {
            "id": note.id,
            "path": note.path,
            "title": note.title,
            "folder": note.folder,
            "score": score,
            "search_type": "keyword",
        }

    def _body_scan_fallback(
        self,
        query: str,
        base_filters: list,
        merged: Dict[int, Dict[str, Any]],
        limit: int,
    ) -> None:
        """Substring-scan .md bodies for notes lacking embedded chunks.

        Reads from VAULT_PATH on demand (per the filesystem-on-demand design).
        Only considers notes with no chunks and not already matched, and stops
        after _FS_SCAN_CAP files or once `limit` results are reached.
        """
        needle = query.lower()
        if not needle:
            return

        embedded_ids = {row[0] for row in self.db.query(EmbeddingChunk.note_id).distinct().all()}

        candidates = (
            self.db.query(Note)
            .filter(*base_filters)
            .order_by(Note.last_indexed_at.desc())
            .limit(_FS_SCAN_CAP)
            .all()
        )

        for note in candidates:
            if len(merged) >= limit:
                break
            if note.id in merged or note.id in embedded_ids:
                continue
            note_file = settings.vault_path / note.path
            try:
                with open(note_file, "r", encoding="utf-8") as f:
                    if needle in f.read().lower():
                        merged[note.id] = self._kw_row(note, 0.7)
            except OSError:
                continue

    def _semantic_search(
        self,
        query_embedding: List[float],
        folder: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Semantic search using pgvector cosine distance on embedding_vec.

        Uses the `<=>` cosine-distance operator (0 = identical, 2 = opposite),
        converts distance to a 0..1 similarity, and returns one row per note
        (the best-matching chunk). Requires the embedding_vec column + data
        created by supabase/bootstrap.sql and the embedding pipeline.
        """
        vec_literal = "[" + ",".join(repr(float(x)) for x in query_embedding) + "]"

        obsidian_clause = (
            "AND (" + " OR ".join([f"n.folder LIKE '{digit}%'" for digit in "0123456789"]) + ") "
            "AND n.folder != '14 Agent Outputs'"
        )
        folder_clause = f"AND n.folder = :folder {obsidian_clause}" if folder else obsidian_clause
        sql = text(f"""
            SELECT n.id AS note_id, n.path, n.title, n.folder,
                   MIN(ec.embedding_vec <=> :vec) AS distance
            FROM embedding_chunks ec
            JOIN notes n ON n.id = ec.note_id
            WHERE ec.embedding_vec IS NOT NULL
              AND ec.is_stale = false
              AND n.is_archived = false
              {folder_clause}
            GROUP BY n.id, n.path, n.title, n.folder
            ORDER BY distance ASC
            LIMIT :limit
        """)

        params = {"vec": vec_literal, "limit": limit}
        if folder:
            params["folder"] = folder

        rows = self.db.execute(sql, params).mappings().all()

        results = []
        for r in rows:
            # cosine distance in [0, 2] -> similarity in [0, 1]
            similarity = max(0.0, 1.0 - (float(r["distance"]) / 2.0))
            results.append({
                "id": r["note_id"],
                "path": r["path"],
                "title": r["title"],
                "folder": r["folder"],
                "score": similarity,
                "search_type": "semantic"
            })
        return results

    def _blend(
        self,
        keyword_results: List[Dict[str, Any]],
        semantic_results: List[Dict[str, Any]],
        keyword_weight: float,
        semantic_weight: float,
        limit: int,
    ) -> List[Dict[str, Any]]:
        """Merge keyword + semantic results by weighted score, keyed by note id."""
        merged: Dict[int, Dict[str, Any]] = {}

        for r in keyword_results:
            merged[r["id"]] = {**r, "score": keyword_weight * r["score"], "search_type": "keyword"}

        for r in semantic_results:
            if r["id"] in merged:
                merged[r["id"]]["score"] += semantic_weight * r["score"]
                merged[r["id"]]["search_type"] = "hybrid"
            else:
                merged[r["id"]] = {**r, "score": semantic_weight * r["score"]}

        ranked = sorted(merged.values(), key=lambda x: x["score"], reverse=True)
        return ranked[:limit]

    def semantic_search_available(self) -> bool:
        """True only when running on Postgres with at least one live vector.

        Guards the pgvector query so local SQLite and un-embedded databases
        fall back to keyword search instead of erroring.
        """
        if "postgres" not in str(self.db.bind.url):
            return False
        try:
            count = self.db.execute(text(
                "SELECT COUNT(*) FROM embedding_chunks WHERE embedding_vec IS NOT NULL"
            )).scalar()
            return bool(count and count > 0)
        except Exception:
            return False
