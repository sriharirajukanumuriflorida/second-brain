# FDE Vault Agent Platform - Frontend

React frontend for the FDE Vault Agent Platform.

## Phase 2 Scope

Phase 2 implements a responsive web UI for the backend indexing and search capabilities:

- React with Vite
- TailwindCSS for styling
- Mobile-responsive design
- API integration with Phase 1 backend
- Note browsing and viewing
- Search interface
- Status dashboard
- Sync trigger UI

## Project Structure

```
frontend/
├── src/
│   ├── main.jsx              # React entry point
│   ├── App.jsx               # Main app component
│   ├── api/
│   │   └── client.js         # API client for backend
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   └── MobileNav.jsx
│   │   ├── notes/
│   │   │   ├── NoteList.jsx
│   │   │   ├── NoteCard.jsx
│   │   │   └── NoteDetail.jsx
│   │   ├── search/
│   │   │   └── SearchBar.jsx
│   │   └── dashboard/
│   │       └── StatusDashboard.jsx
│   ├── pages/
│   │   ├── NotesPage.jsx
│   │   ├── SearchPage.jsx
│   │   └── DashboardPage.jsx
│   └── styles/
│       └── index.css
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js
```

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

3. Build for production:
```bash
npm run build
```

## Environment Variables

Create `.env` file:
```
VITE_API_URL=http://localhost:8000
```

## API Integration

The frontend connects to the Phase 1 backend API:
- GET /health
- POST /api/v1/sync
- GET /api/v1/status
- GET /api/v1/notes
- GET /api/v1/notes/{id}
- GET /api/v1/folders
- GET /api/v1/search
