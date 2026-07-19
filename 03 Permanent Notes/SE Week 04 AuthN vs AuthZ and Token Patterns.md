# SE Week 04 AuthN vs AuthZ and Token Patterns

**Authentication** proves caller identity; **authorization** decides whether that identity may perform an action on a resource. A valid token is not enough — it must have the right audience, issuer, expiry, tenant binding, scopes/roles, and resource permissions.

Common token patterns include API keys for application identity, bearer tokens for user/service principals and scopes, sessions for browser apps, and signed requests or mTLS for higher-assurance integrations. Operational details matter: rotation, revocation, audit logs, least privilege, and clear `401` vs `403` behavior.

> One-liner: **AuthN says who; AuthZ says may they do this here, now.**


Related: [[02 Literature Notes/Software Engineering/APIs, Integration & Backend Engineering]] · [[04 Code Snippets/Software Engineering/SE Week 04 Async Job Queue and SQLite Demo]]
