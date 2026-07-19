# SE Week 04 REST API Design Checklist

A production REST API needs more than routes. Checklist: resource-oriented URLs, correct HTTP methods, precise status codes, typed request/response schemas, consistent error envelope, pagination/filtering rules, idempotency keys for retryable writes, correlation/request ids, auth scopes, rate-limit behavior, examples, and version/deprecation policy.

Handlers should follow a boring sequence: validate input, authenticate, authorize the specific resource/action, call application logic, persist or enqueue work, return a documented response, and emit structured logs. Boring contracts make integrations faster and outages easier to debug.

> One-liner: **an API contract is request shape, response shape, security rule, error rule, and evolution rule.**


Related: [[02 Literature Notes/Software Engineering/APIs, Integration & Backend Engineering]] · [[04 Code Snippets/Software Engineering/SE Week 04 Dataclass API Contract Handler]]
