# Second Brain / FDE Vault Agent Platform

A personal knowledge base built on an Obsidian vault. The app syncs markdown notes from GitHub, indexes them, and exposes search, browsing, status, and chat through a FastAPI backend and a React frontend.

It keeps vault content read-only, supports GitHub OAuth for protected actions, and keeps temporary read-only share links separate for visitors.

## What it does

- Syncs an Obsidian vault from GitHub
- Indexes markdown notes, tags, backlinks, and folders
- Provides keyword and semantic search
- Shows sync and vault status in the UI
- Supports GitHub OAuth login
- Supports temporary read-only share links

## Tech stack

**Frontend**
- React
- Vite
- Tailwind CSS
- Axios
- React Router

**Backend**
- Python
- FastAPI
- SQLAlchemy
- Pydantic
- SQLite for local dev
- PostgreSQL + pgvector for production

**Auth and integrations**
- GitHub OAuth
- GitHub repository sync
- Read-only share links

## Deployment

- **Frontend:** Vercel
- **Backend:** Render
- **Database:** Supabase PostgreSQL
- **CI/CD:** GitHub Actions

## Local development

**Backend**

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

## Environment variables

**Backend**

- `GITHUB_REPO_URL`
- `GITHUB_PAT`
- `GITHUB_OAUTH_CLIENT_ID`
- `GITHUB_OAUTH_CLIENT_SECRET`
- `GITHUB_OAUTH_REDIRECT_URI`
- `DATABASE_URL`
- `VAULT_PATH`
- `LLM_PROVIDER`
- `LLM_API_KEY`
- `LLM_MODEL`
- `EMBEDDING_PROVIDER`
- `EMBEDDING_API_KEY`
- `EMBEDDING_MODEL`
- `CORS_ALLOW_ORIGINS`

**Frontend**

- `VITE_API_URL`

## Project layout

```text
backend/   FastAPI API, auth, sync, indexing, search
frontend/  React UI
```

