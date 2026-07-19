# SE Week 04+ OAuth2 OIDC and Token Patterns

OAuth2 delegates authorization; OIDC adds authentication identity through ID tokens and standard claims. Use Authorization Code + PKCE for user-facing browser/native apps; use Client Credentials for service-to-service workloads. Do not confuse ID tokens with API access tokens.

JWT access tokens are locally verifiable and should be short-lived, audience-bound, issuer-bound, scope-bound, and signed with an allowlisted algorithm/key. Opaque tokens centralize introspection and revocation but add a lookup/cache dependency. Refresh-token rotation issues a new refresh token on each use and invalidates the previous one to detect replay.

Authorization is still separate: RBAC grants broad roles, while ABAC checks tenant, resource, classification, purpose, and environment.

> One-liner: **OAuth2 says what a client may access; OIDC says who the user is; policy says whether this action on this resource is allowed.**


Related: [[02 Literature Notes/Software Engineering/APIs, Integration & Backend Engineering]] · [[04 Code Snippets/Software Engineering/SE Week 04+ OpenTelemetry Retry With Jitter Demo]]
