# FDE Vault Agent Platform — Next Steps

Status snapshot and the remaining work to get from "builds + tested locally" to
"deployed and usable." Grouped by what blocks what.

---

## 0. Security (do first — before any deploy)

- [ ] **Rotate the GitHub PAT** (`ghp_…`) — was exposed in a chat session.
      GitHub → Settings → Developer settings → Personal access tokens → revoke + regenerate.
      Update `GITHUB_PAT` in `.env` and Render.
- [ ] **Rotate the Supabase secret key** (`sb_secret_…`) — was exposed.
      Supabase → Project Settings → API Keys → roll the secret key.
- [ ] Set a strong **`ADMIN_SECRET`** in Render (used to mint read-only links).
- [ ] Confirm `.env` is never committed (it is gitignored today — keep it so).

---

## 1. Deploy

### Database (Supabase) — already coded, needs live verification
- [ ] Run `supabase/bootstrap.sql` in the Supabase SQL Editor (pgvector + RLS + indexes).
- [ ] From a machine **outside the RJF network**, run `python -m scripts.check_supabase`
      with the Session-pooler `DATABASE_URL` — confirm it connects (the RJF network
      blocks the Postgres protocol; that's environmental, not a code issue).
- [ ] Start the backend once against Supabase so `create_all()` builds the tables,
      then re-run `bootstrap.sql` to add the `embedding_vec` column + HNSW index.

### Backend (Render)
- [ ] Deploy `backend/` via `render.yaml`.
- [ ] Set env vars (all `sync: false`): `DATABASE_URL` (Supabase session pooler),
      `LLM_API_KEY`, `EMBEDDING_API_KEY`, `GITHUB_PAT`, `GITHUB_OAUTH_CLIENT_ID`,
      `GITHUB_OAUTH_CLIENT_SECRET`, `GITHUB_OAUTH_REDIRECT_URI`, `CORS_ALLOW_ORIGINS`,
      `ADMIN_SECRET`.
- [ ] Set up the keep-alive pinger against `/health` (see `KEEPALIVE.md`) so the
      free tier doesn't cold-start.

### Frontend (Vercel)
- [ ] Deploy `frontend/`.
- [ ] Set `VITE_API_URL=https://<your-render-app>.onrender.com`.
- [ ] After you know the Vercel URL, set the backend's `CORS_ALLOW_ORIGINS` and
      `GITHUB_OAUTH_REDIRECT_URI` to match it.

### GitHub OAuth
- [ ] Register the OAuth app(s) per `GITHUB_OAUTH_SETUP.md` (one dev, one prod).
- [ ] Ensure the registered callback URL === `GITHUB_OAUTH_REDIRECT_URI` exactly.

---

## 2. Verify end-to-end (post-deploy)
- [ ] `GET /health` returns healthy on Render.
- [ ] Frontend loads on Vercel and reaches the backend (no CORS errors).
- [ ] GitHub login works (owner).
- [ ] Read-only share link works (`SHARED_ACCESS.md`): generate → open incognito →
      read/search only.
- [ ] Vault sync pulls notes; search returns results.
- [ ] Semantic search: after embeddings are generated, confirm `embedding_vec`
      is populated and hybrid results improve (currently unverified at runtime).

---

## 3. Known gaps / follow-ups (not blockers)
- [ ] **Branch naming** deviates from the plan: `generate_branch_name` produces
      `fde/{workflow}/{ts}` with no run-id; the plan specifies
      `agent-output/{workflow}/{ts}-{short_run_id}` for collision safety.
- [ ] **Logout for read-only visitors** clears the cookie (`/access/logout`) but
      there's no admin UI to list/revoke active links — revoke is CLI-only today.
- [ ] **Evaluation-vault fixture** + retrieval-quality regression tests (plan
      Section 3) — needs a live embedding provider.
- [ ] **Frontend tests** — none yet; CI builds the frontend as the only check.
- [ ] **Deprecation cleanup** — FastAPI `on_event` → lifespan; SQLAlchemy 1.x
      `declarative_base` import; pydantic class-based `Config` → `ConfigDict`.
- [ ] **Rate limiting** defaults from the plan (Section 2) aren't all wired to
      every endpoint — audit against `implementationplan.md`.

---

## 4. Deferred by design (later phases)
- Multi-agent orchestration (Phase 8)
- Controlled note promotion (Phase 7)
- Monthly knowledge refresh at scale (Phase 6)
- GitHub App (replacing the prototype PAT)
