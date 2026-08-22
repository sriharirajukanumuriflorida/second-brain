# Connecting the backend to Supabase — end to end

This wires the FastAPI backend to Supabase Postgres (with pgvector for semantic
search). Do the steps in order.

## 0. What was changed in code

- `requirements.txt` — added `psycopg2-binary` (Postgres driver).
- `app/database.py` — the engine now uses pooler-safe settings (pre-ping,
  connection recycling, TCP keepalives). No model changes were needed; the app
  already speaks SQLAlchemy to any Postgres.
- `supabase/bootstrap.sql` — one-time SQL: enables pgvector, adds the real
  `vector(1536)` column + HNSW index, and turns on RLS (defense in depth).
- `scripts/check_supabase.py` — connection smoke test.

## 1. Get the connection string (Transaction pooler)

Supabase Dashboard → your project → **Connect** → **Connection pooling** →
**Transaction** mode. Copy the URI. It looks like:

```
postgresql://postgres.<ref>:<password>@aws-0-<region>.pooler.supabase.com:6543/postgres
```

- Use **port 6543** (transaction pooler), NOT 5432 (direct) — the pooler
  handles many short-lived requests, which is what a web API does.
- Replace `<password>` with your database password (set under Database →
  Settings if you don't have it).
- SQLAlchemy needs the scheme `postgresql://` (Supabase may show
  `postgres://` — either works with psycopg2, but prefer `postgresql://`).

> Keep this string secret. It goes in `.env` locally and in Render's env vars
> (as a `sync: false` secret) — never commit it.

## 2. Run the bootstrap SQL (once)

Supabase Dashboard → **SQL Editor** → paste the contents of
`supabase/bootstrap.sql` → **Run**.

At this point sections 1–2 (pgvector + RLS) apply. The vector column/index
(section 3–5) will no-op until the tables exist — that's expected; you re-run
after step 4.

## 3. Point the app at Supabase locally & test

Set `DATABASE_URL` in `backend/.env` to the pooler URI from step 1, then:

```bash
cd backend
pip install -r requirements.txt          # pulls in psycopg2-binary
python scripts/check_supabase.py         # should connect; tables "not created yet" is fine here
```

Expected: `connected`, `pgvector extension installed: True`, tables listed as
not-created-yet.

## 4. Create the tables

Start the backend once — `init_db()` runs `create_all()` and creates the six
tables:

```bash
uvicorn app.main:app --reload
```

Then stop it and re-run the smoke test — it should now list all tables:

```bash
python scripts/check_supabase.py         # tables present; embedding_vec: False (added next)
```

## 5. Finish the vector setup

Back in the Supabase **SQL Editor**, re-run `supabase/bootstrap.sql` (all of
it). Now sections 3–5 add the `embedding_vec` column, the HNSW index, and the
supporting b-tree indexes, and section 2 re-locks the new tables with RLS.

Re-run the smoke test — `embedding_vec vector column: True`.

## 6. Deploy

In Render, set `DATABASE_URL` (this same pooler URI) as a `sync: false` env var.
The app connects on boot. Done.

---

### Note on semantic search

Semantic + hybrid search is **implemented**. `GET /search` embeds the query and
blends pgvector cosine similarity (`embedding_vec <=> query`) with keyword
matching. It activates automatically when:

1. `EMBEDDING_API_KEY` is set (a real key, not the placeholder), AND
2. the DB is Postgres with at least one populated `embedding_vec` row.

Otherwise it degrades cleanly to keyword-only — so it works on local SQLite too.
Pass `?semantic=false` to force keyword-only. The embedding write path
(`embedding_service.py`) now populates `embedding_vec` on Postgres; run the
embeddings pipeline after `bootstrap.sql` so vectors exist to search.
