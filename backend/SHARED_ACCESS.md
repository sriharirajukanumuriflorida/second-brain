# Read-only shared access (24h links)

Share your knowledge base with someone **without giving them a GitHub account**.
You mint a temporary link; opening it claims the link and grants read-only
access for 24 hours.

## How it works

```
You run the generator (with ADMIN_SECRET) ──► get a link:
    https://<your-app>.vercel.app/access?token=<random>

You send the link ──► recipient opens it ──►
    backend starts a 24h clock. The browser stores the claimed token and can
    use it for read requests even if cookies are blocked. They can READ/SEARCH
    notes + view dashboards. All writes/workflows are blocked. After 24h it
    expires.
```

**Security properties**
- ✅ Expires 24h after first open (`ttl_hours`, default 24)
- ✅ Read-only — write/workflow endpoints require a real login, which visitors don't have
- ✅ Revocable — see below
- ⚠️ Not hardware-locked. Browsers cannot read a MAC address; "one machine" is
  approximated by the claimed token. Within 24h the browser that claimed the
  link keeps access.

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

Revoking kills active access immediately. Use the Python one-liner:

```bash
python -c "from app.database import SessionLocal; from app.services.auth.access_service import AccessTokenService; AccessTokenService(SessionLocal()).revoke('<token-from-link>')"
```

## Requirements for it to work in production

- `CORS_ALLOW_ORIGINS` must include your exact Vercel origin (cookies + credentials).
- `COOKIE_SECURE=true` in production (HTTPS).
- Frontend must call the API with credentials — already set (`withCredentials: true`).
