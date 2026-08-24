"""
Token budget and cost-minimization utilities for the chat feature.

Skills provided:
  select_context   — trim vault notes to a token budget
  summarize_history — compress old chat turns via a cheap model
  route_model       — pick cheap vs powerful model based on query complexity
  get_or_set_cache  — 1-hour DB-backed reply cache
"""
import hashlib
import json
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Any, Callable, Awaitable

from sqlalchemy.orm import Session
from app.models import Note, ChatCache

# Rough token estimator: 1 token ≈ 4 characters
_CHARS_PER_TOKEN = 4

# Cheap summarisation models
_CHEAP = {
    "anthropic": "claude-3-5-haiku-20241022",
    "openai":    "gpt-4o-mini",
}

# Threshold above which a query is considered "complex" (multi-concept)
_COMPLEXITY_KEYWORDS = [
    "compare", "difference", "architecture", "implement", "design",
    "explain in depth", "how does", "trade-off", "pros and cons",
    "system design", "research",
]


def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // _CHARS_PER_TOKEN)


class TokenBudgetService:
    """Cost-minimization skills for the mentor chat workflow."""

    def __init__(self, db: Session):
        self.db = db

    # ── 1. Context selection ────────────────────────────────────────────────

    def select_context(
        self,
        notes: List[dict],
        max_tokens: int = 2000,
        min_score: float = 0.7,
        max_notes: int = 5,
    ) -> List[dict]:
        """Return at most `max_notes` notes whose score ≥ min_score,
        truncated so that total vault context stays within `max_tokens`."""
        qualified = [n for n in notes if n.get("score", 1.0) >= min_score]
        qualified = qualified[:max_notes]

        selected: List[dict] = []
        used_tokens = 0
        for note in qualified:
            content = note.get("content") or note.get("title", "")
            tokens = _estimate_tokens(content)
            if used_tokens + tokens > max_tokens:
                # Try to include a truncated version
                allowed_chars = (max_tokens - used_tokens) * _CHARS_PER_TOKEN
                if allowed_chars > 200:
                    note = dict(note)
                    note["content"] = content[:allowed_chars] + "…"
                    selected.append(note)
                break
            selected.append(note)
            used_tokens += tokens

        return selected

    # ── 2. History summarisation ────────────────────────────────────────────

    async def summarize_history(
        self,
        messages: List[dict],
        keep_recent: int = 4,
        llm_provider=None,
    ) -> List[dict]:
        """Keep the last `keep_recent` turns verbatim.
        Older turns are compressed into a single summary assistant message.
        If no llm_provider is supplied, older turns are simply dropped."""
        if len(messages) <= keep_recent:
            return messages

        old_turns = messages[:-keep_recent]
        recent = messages[-keep_recent:]

        if llm_provider is None:
            # Fallback: drop old turns
            return recent

        # Build a cheap summarisation request
        from app.services.llm.base import LLMMessage
        history_text = "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in old_turns
        )
        summary_messages = [
            LLMMessage(
                role="system",
                content="Summarise the following conversation in 3-5 bullet points "
                        "focusing on what the learner asked and what was explained. "
                        "Be concise.",
            ),
            LLMMessage(role="user", content=history_text),
        ]

        try:
            resp = await llm_provider.generate(summary_messages, max_tokens=300, temperature=0.3)
            summary_msg = {"role": "assistant", "content": f"[Earlier conversation summary]\n{resp.content}"}
            return [summary_msg] + recent
        except Exception:
            return recent  # graceful degradation

    # ── 3. Model routing ────────────────────────────────────────────────────

    def route_model(self, query: str, provider: str) -> str:
        """Model routing is disabled — always returns None so the caller's
        configured model is used. Cheap-model routing caused 404s on accounts
        that don't have access to smaller models."""
        return None

    # ── 4. Reply cache ──────────────────────────────────────────────────────

    def _make_cache_key(self, query: str, note_paths: List[str]) -> str:
        top3 = sorted(note_paths)[:3]
        raw = query.strip().lower() + "|" + "|".join(top3)
        return hashlib.sha256(raw.encode()).hexdigest()

    def get_cache(self, query: str, note_paths: List[str]) -> Optional[dict]:
        """Return a cached reply dict or None."""
        key = self._make_cache_key(query, note_paths)
        row = self.db.query(ChatCache).filter(ChatCache.cache_key == key).first()
        if row is None:
            return None
        # Normalise expires_at to tz-aware
        expires = row.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires <= datetime.now(timezone.utc):
            self.db.delete(row)
            self.db.commit()
            return None
        return {
            "reply": row.reply,
            "source_notes": json.loads(row.source_notes or "[]"),
            "web_sources": json.loads(row.web_sources or "[]"),
        }

    def set_cache(
        self,
        query: str,
        note_paths: List[str],
        reply: str,
        source_notes: List[str],
        web_sources: List[dict],
        ttl_hours: int = 1,
    ) -> None:
        """Store a reply in the cache."""
        key = self._make_cache_key(query, note_paths)
        now = datetime.now(timezone.utc)
        # Upsert
        row = self.db.query(ChatCache).filter(ChatCache.cache_key == key).first()
        if row is None:
            row = ChatCache(cache_key=key)
            self.db.add(row)
        row.reply = reply
        row.source_notes = json.dumps(source_notes)
        row.web_sources = json.dumps(web_sources)
        row.created_at = now
        row.expires_at = now + timedelta(hours=ttl_hours)
        self.db.commit()
