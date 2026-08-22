-- =============================================================================
-- Supabase bootstrap for FDE Vault Agent Platform
-- =============================================================================
-- Run this ONCE against your Supabase project BEFORE the backend first boots.
--   Supabase Dashboard → SQL Editor → paste → Run
--
-- Why this exists:
--   The app creates ordinary tables at startup via SQLAlchemy's
--   Base.metadata.create_all(). But create_all() CANNOT:
--     1. enable the pgvector extension,
--     2. create a real `vector(1536)` column for semantic search,
--     3. build the HNSW index that makes vector search fast,
--     4. enable Row-Level Security.
--   This script does those four things. It is idempotent — safe to re-run.
--
-- Order of operations:
--   1. Run THIS script (creates extension + RLS-ready public schema).
--   2. Start the backend → create_all() creates any missing plain tables.
--   3. Run the "post-create_all" section at the bottom to add the vector
--      column + index to the embedding_chunks table create_all() just made.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- 1. Extensions
-- -----------------------------------------------------------------------------
-- pgvector powers semantic search. On Supabase the extension is named "vector".
create extension if not exists vector with schema extensions;


-- -----------------------------------------------------------------------------
-- 2. Row-Level Security — defense in depth
-- -----------------------------------------------------------------------------
-- The backend connects with the full Postgres role via the pooler, so RLS does
-- NOT restrict it. But every table in the `public` schema can be reachable
-- through Supabase's Data (REST) API if the anon/authenticated roles are
-- granted access. Enabling RLS with NO policies = deny-all to those roles,
-- which is exactly what we want for a server-only app.
--
-- This block enables RLS on every existing public table. Re-run it AFTER the
-- backend has booted (so it also covers tables create_all() made). It is safe
-- to run repeatedly.
do $$
declare
  r record;
begin
  for r in
    select tablename
    from pg_tables
    where schemaname = 'public'
  loop
    execute format('alter table public.%I enable row level security;', r.tablename);
    -- No policies are created on purpose: RLS-on + zero-policies denies all
    -- anon/authenticated access while leaving the backend's privileged role
    -- (which bypasses RLS) fully functional.
  end loop;
end $$;


-- =============================================================================
-- POST create_all() SECTION
-- =============================================================================
-- Run everything BELOW this line AFTER the backend has started at least once
-- (so the embedding_chunks table exists). Safe to re-run.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 3. Real vector column for embeddings
-- -----------------------------------------------------------------------------
-- The SQLAlchemy model declares `embedding` as LargeBinary (bytea) because
-- SQLAlchemy has no native pgvector type here. For semantic search we add a
-- proper vector column alongside it. Dimension 1536 = OpenAI
-- text-embedding-3-small (see app/services/embeddings/openai_embeddings.py).
--
-- If you switch to text-embedding-3-large, change 1536 -> 3072 and rebuild the
-- index. HNSW supports up to 2000 dims per column for some ops, so 3072 needs
-- halfvec — ask before switching.
alter table public.embedding_chunks
  add column if not exists embedding_vec vector(1536);

-- -----------------------------------------------------------------------------
-- 4. HNSW index for fast cosine similarity search
-- -----------------------------------------------------------------------------
-- HNSW gives fast approximate nearest-neighbour search. cosine distance (<=>)
-- matches how OpenAI embeddings are compared. Build this only after data loads
-- for best results, but creating it empty is fine too.
create index if not exists embedding_chunks_embedding_vec_hnsw
  on public.embedding_chunks
  using hnsw (embedding_vec vector_cosine_ops);

-- -----------------------------------------------------------------------------
-- 5. Supporting b-tree indexes the ORM relies on for filtering
-- -----------------------------------------------------------------------------
-- These mirror the indexed columns in the SQLAlchemy models and speed up the
-- keyword-search and staleness queries in hybrid_search / embedding_service.
create index if not exists notes_folder_idx        on public.notes (folder);
create index if not exists notes_is_archived_idx    on public.notes (is_archived);
create index if not exists embedding_chunks_note_id_idx on public.embedding_chunks (note_id);
create index if not exists embedding_chunks_is_stale_idx on public.embedding_chunks (is_stale);
create index if not exists sessions_expires_at_idx  on public.sessions (expires_at);

-- -----------------------------------------------------------------------------
-- Done. Re-run section 2 (RLS loop) now so the tables create_all() made are
-- also locked down.
-- -----------------------------------------------------------------------------
