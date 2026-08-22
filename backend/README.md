# FDE Vault Agent Platform - Backend

FastAPI backend for the FDE Vault Agent Platform.

## Phase 1 Scope

Phase 1 implements read-only vault indexing and keyword search:

- FastAPI application
- SQLite database for metadata
- GitHub repository sync/clone
- Markdown file scanner
- YAML front matter parser
- Tag extractor
- Backlink extractor
- File hash calculation
- Metadata index
- Keyword search
- Audit logging
- API endpoints

## Phase 1 Constraints

- NO LLM calls
- NO vault writes
- Local SQLite database (PostgreSQL for cloud deployment later)
- Read-only indexing

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── database.py          # Database connection and schema
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── services/
│   │   ├── github_service.py    # GitHub sync/clone
│   │   ├── scanner_service.py   # Markdown scanner
│   │   ├── parser_service.py    # YAML front matter parser
│   │   ├── extractor_service.py # Tag/backlink extractor
│   │   ├── hash_service.py      # File hash calculation
│   │   ├── index_service.py     # Metadata index
│   │   └── search_service.py    # Keyword search
│   ├── api/
│   │   ├── __init__.py
│   │   ├── health.py        # Health check endpoint
│   │   ├── sync.py          # Sync endpoints
│   │   ├── status.py        # Status endpoints
│   │   ├── notes.py         # Note endpoints
│   │   ├── folders.py       # Folder endpoints
│   │   └── search.py        # Search endpoints
│   └── utils/
│       ├── logger.py        # Audit logging
│       └── validators.py    # Path and content validators
├── tests/
│   ├── __init__.py
│   ├── test_parser.py
│   ├── test_extractor.py
│   └── test_index.py
├── requirements.txt
└── README.md
```

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

- `GET /health` - Health check
- `POST /api/v1/sync` - Trigger vault sync
- `GET /api/v1/status` - Get sync/index status
- `GET /api/v1/notes` - List notes
- `GET /api/v1/notes/{note_id}` - Get note details
- `GET /api/v1/folders` - List folders
- `GET /api/v1/search` - Keyword search

## Environment Variables

- `GITHUB_REPO_URL` - GitHub repository URL
- `GITHUB_PAT` - GitHub Personal Access Token (for prototype)
- `VAULT_PATH` - Path to local vault clone
- `DATABASE_URL` - SQLite database path (default: sqlite:///./vault.db)
