# SE Week 01 Testing Pyramid and Delivery Strategy

A healthy test strategy optimizes for fast, trustworthy feedback. Unit tests cover pure rules and edge cases; contract tests protect interfaces between modules/services; integration tests verify real adapters; a small set of end-to-end tests covers critical user journeys. The pyramid is not about test prestige — it is about keeping most failures cheap to diagnose.

Delivery discipline completes the loop: small PRs, CI that runs lint/test/build, build-once artifacts, environment-specific configuration, safe migrations, feature flags where useful, and rollback instructions. If tests and CI are slow or flaky, teams route around them.

> One-liner: **ship small changes behind fast feedback** — most tests local and deterministic, few tests broad and expensive.


Related: [[02 Literature Notes/Software Engineering/Software Engineering Refresh]] · [[04 Code Snippets/Software Engineering/SE Week 01 Structured Logging and Error Boundary]]
