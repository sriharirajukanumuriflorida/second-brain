# Read-only shared access (24h links)

Share your knowledge base with someone **without giving them a GitHub account**.
You mint a one-time link; the first person to open it gets read-only access
bound to their browser for 24 hours.

## How it works

```
You run the generator (with ADMIN_SECRET) ──► get a link:
    https://<your-app>.vercel.app/access?token=<random>

You send the link ──► recipient opens it ──►
    backend binds it to their browser (HTTP-only cookie), starts a 24h clock,
    marks the link used (single-use). They can READ/SEARCH notes + view
    dashboards. All writes/workflows are blocked. After 24h it expires.
```

**Security properties**
- ✅ Expires 24h after first open (`ttl_hours`, default 24)
- ✅ Read-only — write/workflow endpoints require a real login, which visitors don't have
- ✅ Single-use — the link binds to the first browser; a second claim is rejected
- ✅ Revocable — see below
- ⚠️ Not hardware-locked. Browsers cannot read a MAC address; "one machine" is
  approximated by the per-browser cookie. Within 24h the *claimed browser* keeps
  access; the original link is dead after claim.

## Generate a link

Set a strong `ADMIN_SECRET` in `.env` (and Render), then from `backend/`:

```bash
python -m scripts.generate_access_link \
    --secret "$ADMIN_SECRET" \
    --base-url https://<your-app>.vercel.app \
    --hours 24 \
    --label "for Alex"
```

It prints the share link. Send that to the recipient.

## Revoke early

Revoking kills active access immediately. Currently via a quick Python one-liner
(or add an admin endpoint later):

```bash
python -c "from app.database import SessionLocal; from app.services.auth.access_service import AccessTokenService; AccessTokenService(SessionLocal()).revoke('<token-from-link>')"
```

## Requirements for it to work in production

- `CORS_ALLOW_ORIGINS` must include your exact Vercel origin (cookies + credentials).
- `COOKIE_SECURE=true` in production (HTTPS).
- Frontend must call the API with credentials — already set (`withCredentials: true`).
