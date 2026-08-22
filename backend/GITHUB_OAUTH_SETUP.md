# GitHub OAuth setup

The backend authenticates users via GitHub OAuth (see `app/api/auth.py` and
`app/services/auth/oauth_service.py`). This guide registers the OAuth app and
wires the matching redirect URI. No secrets are committed — everything goes in
`.env` (local) and Render env vars (prod).

## How the flow works (so the redirect URI makes sense)

```
1. Frontend calls  GET  {backend}/api/v1/auth/github/login  -> returns auth_url + state
2. Browser visits GitHub, user authorizes
3. GitHub redirects to your REGISTERED redirect URI with ?code=...&state=...
4. That page calls POST {backend}/api/v1/auth/github/callback?code=...&state=...
5. Backend exchanges code for a token, creates a user + session, returns a bearer token
```

The **registered redirect URI in GitHub must exactly match** the
`GITHUB_OAUTH_REDIRECT_URI` value the backend is configured with — protocol,
host, path, and (if any) trailing slash. A mismatch is the #1 cause of
`redirect_uri_mismatch` errors.

## 1. Register the OAuth app on GitHub

GitHub → **Settings → Developer settings → OAuth Apps → New OAuth App**
(https://github.com/settings/developers)

| Field | Local dev value | Production value |
|-------|-----------------|------------------|
| Application name | `FDE Vault (dev)` | `FDE Vault` |
| Homepage URL | `http://localhost:5173` | `https://<your-app>.vercel.app` |
| Authorization callback URL | `http://localhost:5173/auth/callback` | `https://<your-app>.vercel.app/auth/callback` |

> Register **two separate OAuth apps** (one dev, one prod) so local and
> deployed callbacks don't collide. Each gives its own Client ID + secret.

After creating, click **Generate a new client secret** and copy both the
**Client ID** and **Client secret** immediately.

## 2. Set the values

### Local — `backend/.env`
```
GITHUB_OAUTH_CLIENT_ID=<dev client id>
GITHUB_OAUTH_CLIENT_SECRET=<dev client secret>
GITHUB_OAUTH_REDIRECT_URI=http://localhost:5173/auth/callback
```

### Production — Render dashboard (env vars, all `sync: false`)
```
GITHUB_OAUTH_CLIENT_ID=<prod client id>
GITHUB_OAUTH_CLIENT_SECRET=<prod client secret>
GITHUB_OAUTH_REDIRECT_URI=https://<your-app>.vercel.app/auth/callback
```

Also set `CORS_ALLOW_ORIGINS` to the same frontend origin(s), e.g.
`https://<your-app>.vercel.app,http://localhost:5173` — otherwise the browser
blocks the frontend→backend calls.

## 3. The redirect page

The callback URL points at the **frontend** (`/auth/callback`). That frontend
route must read `code` + `state` from the query string and POST them to the
backend:

```
POST {backend}/api/v1/auth/github/callback?code=<code>&state=<state>
```

The backend returns `{ access_token, user }`. Store the `access_token` and send
it as `Authorization: Bearer <token>` on subsequent API calls.

> If you'd rather have GitHub call the backend directly, register the callback
> as `{backend}/api/v1/auth/github/callback` instead and have the backend
> redirect to the frontend after issuing the session. Either works — just keep
> the registered URI and `GITHUB_OAUTH_REDIRECT_URI` identical.

## 4. Verify

1. Start backend + frontend locally.
2. Click login → you should land on GitHub's authorize screen.
3. Authorize → you should be redirected back and end up logged in.
4. `redirect_uri_mismatch` → the registered callback URL and
   `GITHUB_OAUTH_REDIRECT_URI` don't match exactly. Fix one to match the other.
