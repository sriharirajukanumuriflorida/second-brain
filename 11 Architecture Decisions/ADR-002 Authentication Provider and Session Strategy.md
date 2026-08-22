# ADR-002: Authentication Provider and Session Strategy

## Status
Approved

## Owner
Hari Kanumuri

## Date
2026-07-24

## Context
The FDE Vault Agent Platform requires secure authentication to protect private knowledge. The platform must support mobile access, integrate with GitHub-centric workflow, and avoid custom username/password implementation in MVP. Session management must balance security with usability across desktop and phone browsers.

## Decision
**Selected Provider: GitHub OAuth**
- Use GitHub OAuth for personal GitHub-backed MVP
- Microsoft Entra ID or Auth0 may be considered later if enterprise alignment or multi-provider support is required

**Session Management:**
- Secure HTTP-only cookies for browser-based sessions
- Short-lived access sessions
- Refresh token strategy only if required by chosen auth provider
- Server-side session invalidation support
- Logout endpoint
- CSRF protection if cookie-based auth is used

## Alternatives Considered

### Custom Username/Password
- **Pros:** Full control, no external dependency
- **Cons:** Security burden, password management, not aligned with MVP goals, rejected per plan

### JWT-Only Stateless
- **Pros:** Scalable, stateless
- **Cons:** Token revocation complexity, CSRF risk, less secure for browser-based apps

### Session-Only Without Refresh
- **Pros:** Simpler implementation
- **Cons:** Poor UX, frequent re-authentication required

## Consequences
- No custom username/password authentication in MVP
- Authentication is delegated to trusted identity provider
- Session security is managed through HTTP-only cookies
- CSRF protection required for cookie-based auth
- Logout capability is mandatory
- Session invalidation must be server-side

## Cost Impact
- GitHub OAuth: free for personal use
- Microsoft Entra ID: potential cost depending on tier
- Auth0: cost scales with users
- No additional infrastructure cost for auth itself

## Security Impact
- Delegated authentication reduces security burden
- HTTP-only cookies prevent XSS token theft
- CSRF protection prevents cross-site request forgery
- Server-side session invalidation enables immediate revocation
- No password storage eliminates credential breach risk
- Identity provider handles security best practices

## Operational Impact
- Identity provider manages user accounts
- Session management is centralized
- Logout is simple and reliable
- Session monitoring can leverage identity provider logs
- Rate limiting can be integrated with auth provider
- Mobile browser compatibility is ensured through standard OAuth flow

## Follow-Up Actions
- [x] Select GitHub OAuth as authentication provider
- [ ] Register OAuth application with GitHub
- [ ] Configure callback URLs for production and staging
- [ ] Implement HTTP-only cookie session handling
- [ ] Implement CSRF protection
- [ ] Implement logout endpoint with server-side invalidation
- [ ] Test mobile browser authentication flow
