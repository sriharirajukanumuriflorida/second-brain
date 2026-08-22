"""
Supabase connection smoke test.

Verifies the backend can actually connect to Supabase Postgres through the
pooler, that pgvector is installed, and that the app's tables exist. Run this
locally BEFORE deploying to Render so a bad DATABASE_URL fails here, not in prod.

Usage:
    # Reads DATABASE_URL from the environment (or backend/.env)
    python scripts/check_supabase.py

Exit code 0 = all good, 1 = something failed.
"""
import sys
from sqlalchemy import text

# Reuse the app's engine so we test the EXACT connection config the app uses
# (prepared-statement handling, pool settings, etc.), not a fresh one.
from app.config import settings
from app.database import engine


def main() -> int:
    url = settings.database_url
    masked = url
    if "@" in url and "//" in url:
        # mask credentials for safe printing: scheme://user:pass@host -> scheme://***@host
        scheme, rest = url.split("//", 1)
        if "@" in rest:
            masked = f"{scheme}//***@{rest.split('@', 1)[1]}"
    print(f"DATABASE_URL: {masked}")

    if "sqlite" in url:
        print("WARNING: still pointing at SQLite, not Supabase. Set DATABASE_URL.")
        return 1

    try:
        with engine.connect() as conn:
            # 1. Basic connectivity + server version
            version = conn.execute(text("select version();")).scalar()
            print(f"[ok] connected: {version.split(',')[0]}")

            # 2. pgvector present?
            has_vector = conn.execute(text(
                "select exists (select 1 from pg_extension where extname = 'vector');"
            )).scalar()
            print(f"[{'ok' if has_vector else 'MISSING'}] pgvector extension installed: {has_vector}")

            # 3. App tables present?
            expected = {
                "notes", "sync_events", "audit_logs",
                "embedding_chunks", "users", "sessions",
            }
            rows = conn.execute(text(
                "select tablename from pg_tables where schemaname = 'public';"
            )).scalars().all()
            present = set(rows)
            missing = expected - present
            print(f"[info] public tables found: {sorted(present) or '(none yet)'}")
            if missing:
                print(f"[info] not created yet (start the backend once): {sorted(missing)}")

            # 4. vector column present on embedding_chunks?
            if "embedding_chunks" in present:
                has_vec_col = conn.execute(text(
                    "select exists (select 1 from information_schema.columns "
                    "where table_schema='public' and table_name='embedding_chunks' "
                    "and column_name='embedding_vec');"
                )).scalar()
                print(f"[{'ok' if has_vec_col else 'TODO'}] embedding_vec vector column: {has_vec_col}")

        if not has_vector:
            print("\nFAIL: run supabase/bootstrap.sql in the Supabase SQL Editor first.")
            return 1
        print("\nAll connection checks passed.")
        return 0

    except Exception as e:  # noqa: BLE001 - smoke test wants the raw error
        print(f"\nFAIL: could not connect / query: {type(e).__name__}: {e}")
        print("Check: DATABASE_URL host/password, and that you used the "
              "Transaction pooler URI (port 6543), not the direct connection.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
