"""
Hybrid search service (keyword + semantic).
"""
from typing import List, Dict, Any, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.models import Note, EmbeddingChunk


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
        """Keyword search over note title and frontmatter."""
        db_query = self.db.query(Note).filter(Note.is_archived == False)

        if folder:
            db_query = db_query.filter(Note.folder == folder)

        search_pattern = f"%{query}%"
        db_query = db_query.filter(
            (Note.title.ilike(search_pattern)) |
            (Note.frontmatter.ilike(search_pattern))
        )

        results = db_query.limit(limit).all()

        return [
            {
                "id": note.id,
                "path": note.path,
                "title": note.title,
                "folder": note.folder,
                "score": 1.0,
                "search_type": "keyword"
            }
            for note in results
        ]

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

        folder_clause = "AND n.folder = :folder" if folder else ""
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
