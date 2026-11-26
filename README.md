# Second Brain / FDE Vault Agent Platform

A personal knowledge and learning platform built around an Obsidian vault. It syncs Markdown notes from GitHub, indexes them for search, and adds a mentor chat, learning progress, quizzes, and AI-assisted workflows.

## Features

- **Vault sync and browsing:** Clone or update a GitHub-hosted vault; index note metadata, tags, backlinks, and folders.
- **Search and discovery:** Search note titles, metadata, and content. PostgreSQL with pgvector adds semantic search and related-note recommendations; SQLite falls back to keyword search.
- **Mentor Chat:** Ask questions with vault search context, optional web search, configurable Anthropic or OpenAI models, session usage estimates, and a reply cache.
- **Learning progress and quizzes:** Track registered topics by phase, mark topics complete, and practice interview-style questions extracted from notes. An LLM scores answers and provides feedback.
- **Agent workflows:** Generate implementation plans, solution briefs, knowledge refreshes, technology radar outputs, and other drafts through admin-only APIs.
- **Wiki compaction:** Compile source notes into a derived page, preview it, or create a pull request under `14 Agent Outputs/`.
- **MCP server:** Connect compatible clients to read-only tools for searching and fetching notes and finding related notes.
- **Access controls:** GitHub OAuth for users and revocable, time-limited share links for visitors.

## How it works

```text
GitHub vault
    |
    v
Sync + Markdown indexing
    |
    +-- Keyword search
    +-- Optional embeddings -> PostgreSQL / pgvector -> semantic search
    +-- Mentor Chat and learning workflows -> LLM provider
    +-- Read-only MCP tools -> compatible clients
```

The FastAPI backend serves the React frontend and API. Vault source notes remain the source of truth; admin workflows can produce separate drafts and propose generated output through a GitHub pull request.

## Technology

| Component | Technology |
|---|---|
| Frontend | React, Vite, Tailwind CSS |
| Backend | Python, FastAPI, SQLAlchemy |
| Database | SQLite locally; PostgreSQL and pgvector for semantic search |
| AI | Anthropic or OpenAI for generation; OpenAI embeddings |
| Integrations | GitHub OAuth, GitHub sync and pull requests, MCP |
| Deployment | Render, Vercel, Supabase; GitHub Actions |

## Getting started

### Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- Git
- A GitHub OAuth app for sign-in
- A GitHub-hosted Markdown vault
- API keys for any LLM or embedding features you want to use

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create `backend/.env` with your configuration. For example:

```dotenv
GITHUB_REPO_URL=https://github.com/<owner>/<vault-repo>.git
GITHUB_OAUTH_CLIENT_ID=<client-id>
GITHUB_OAUTH_CLIENT_SECRET=<client-secret>
GITHUB_OAUTH_REDIRECT_URI=http://localhost:5173/auth/callback

LLM_PROVIDER=anthropic
LLM_API_KEY=<provider-api-key>
LLM_MODEL=claude-haiku-4-5

CORS_ALLOW_ORIGINS=http://localhost:5173
```

Then start the API:

```bash
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`; interactive API documentation is available at `http://localhost:8000/docs`. SQLite is the default database.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open the Vite URL, normally `http://localhost:5173`, and sign in with GitHub. The OAuth app's callback URL must exactly match `GITHUB_OAUTH_REDIRECT_URI`.

New users are created with the `user` role. **Sync, embedding management, and agent workflows require an admin role**; an existing account must be promoted separately using the backend's user-management service or database administration. The repository does not currently provide an admin bootstrap UI.

See [GitHub OAuth setup](backend/GITHUB_OAUTH_SETUP.md) for details.

## Configuration

| Variable | Purpose |
|---|---|
| `GITHUB_REPO_URL` | Git URL of the vault to sync |
| `GITHUB_PAT` | GitHub token for supported GitHub operations |
| `GITHUB_OAUTH_CLIENT_ID`, `GITHUB_OAUTH_CLIENT_SECRET` | GitHub OAuth app credentials |
| `GITHUB_OAUTH_REDIRECT_URI` | Frontend OAuth callback URL |
| `DATABASE_URL` | SQLite or PostgreSQL connection string |
| `VAULT_PATH` | Local path for the vault clone |
| `AUTO_SYNC_ON_STARTUP` | Re-sync on startup; useful with ephemeral storage |
| `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL` | Default generation provider, key, and model |
| `EMBEDDING_PROVIDER`, `EMBEDDING_API_KEY`, `EMBEDDING_MODEL` | Embedding configuration |
| `CORS_ALLOW_ORIGINS` | Comma-separated allowed frontend origins |
| `ADMIN_SECRET` | Secret used by the share-link CLI |
| `COOKIE_SECURE` | Require HTTPS for the shared-access cookie |
| `VITE_API_URL` | Backend URL used by the frontend |

Do not commit credentials. Private vault cloning also requires Git authentication available to the backend environment.

## Search and embeddings

Keyword search works without pgvector. Hybrid search requires PostgreSQL, the pgvector setup, an embedding API key, and populated vectors. Changed notes can be embedded during sync; admins can also manage and backfill embeddings.

See [Supabase setup](backend/SUPABASE_SETUP.md) for database bootstrap and vector configuration. Changing embedding models requires care: existing and new vectors must be compatible.

## Mentor Chat and learning

Mentor Chat supports provider/model settings, optional web search, source-note paths, and commands such as `/help`, `/models`, `/model`, `/usage`, and `/web on`. The Progress page tracks registered topics and lets signed-in users drill available note-based questions.

**Current limitation:** Mentor Chat's search results currently provide note metadata to the chat workflow, but the normal search path does not populate note bodies in those results. Treat its answers as LLM-generated assistance, not guaranteed answers grounded in full note content.

## MCP integration

From `backend/`, with dependencies and database/vault configuration in place:

```bash
python -m mcp_server.server
```

The stdio server exposes `search_notes`, `fetch_note`, and `related_notes`. It reads from the configured database and vault; related-note recommendations require suitable pgvector data. The current MCP search call uses keyword search.

## Access, privacy, and cost

- Share links grant time-limited read access; progress changes and admin workflows require a signed-in user or admin, respectively. See [shared access](backend/SHARED_ACCESS.md).
- Chat, embeddings, quizzes, and workflows may send prompts or note content to external AI providers and can incur API charges. These integrations do not run a local model.
- User-supplied chat API keys are stored in browser local storage and sent to the backend with requests. Use only a trusted browser and deployment.
- Token and cost figures are **estimates**, not authoritative provider billing. Check your provider dashboard.
- Review generated answers and pull requests before relying on or merging them.

## Development

```bash
# Backend tests
cd backend
pytest

# Frontend build
cd ../frontend
npm run build
```

The GitHub Actions workflow runs backend checks and a frontend build. The deployment configuration targets Render, Vercel, and Supabase; see [Deployment](DEPLOYMENT.md), [Supabase setup](backend/SUPABASE_SETUP.md), and [Backup and restore](BACKUP_RESTORE.md).

## Project layout

```text
backend/                     FastAPI API, services, MCP server, and tests
frontend/                    React application
00 Inbox/ ... 13 Governance/ Obsidian vault content
14 Agent Outputs/            Generated drafts
implementationguide/         Implementation documentation
scripts/                     Repository utilities
```

## Screenshots

[Dashboard](https://github.com/user-attachments/assets/ecf2a61b-a9e8-42f3-b907-d5dc70dd5780) | [Search](https://github.com/user-attachments/assets/94d1077c-e371-4a02-8b25-bd7b5392980f) | [Notes](https://github.com/user-attachments/assets/dc555452-5be6-488b-a3a5-1c28ad0174ed) | [Mentor Chat](https://github.com/user-attachments/assets/a310c295-cdf9-45e9-9355-76e0c31c5623)

## License

[MIT](LICENSE)
