# SE Week 04+ Production API Design Checklist

Production API checklist:

1. Contract-first OpenAPI 3.1 + JSON Schema with examples and error envelopes.
2. Pydantic v2 request/response models with `extra='forbid'`, field constraints, and separate DB/domain models.
3. AuthN/AuthZ: OAuth2/OIDC flow, token type, issuer, audience, expiry, scopes, tenant binding, RBAC/ABAC policy.
4. Safe writes: Idempotency-Key, `202 + job_id` for slow work, stable status resources, and duplicate-body conflict handling.
5. Safe reads: cursor pagination, bounded limits, ETags, conditional requests, cache headers, and stable ordering.
6. Operations: per-tenant rate limits, retry guidance with jitter, request ids, OpenTelemetry spans, logs, metrics, and documented deprecation/versioning.
7. Database safety: pooled connections, transactions, isolation choice, locking/version columns, N+1 prevention, and migration plan.

> One-liner: **an API is not production until clients can retry it, page through it, authorize it, observe it, and evolve it safely.**


Related: [[02 Literature Notes/Software Engineering/APIs, Integration & Backend Engineering]] · [[04 Code Snippets/Software Engineering/SE Week 04+ FastAPI JWT Rate Limit Idempotency Demo]]
