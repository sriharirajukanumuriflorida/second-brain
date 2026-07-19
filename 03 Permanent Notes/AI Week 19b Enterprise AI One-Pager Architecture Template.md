# AI Week 19b Enterprise AI One-Pager Architecture Template

Reusable one-page structure for an enterprise AI architecture:

1. Business request and clarified problem statement.
2. Users, workflow step, source systems, constraints, and success metrics.
3. Current-state workflow in 5 to 8 bullets.
4. Future-state C4 Container diagram with trust boundary, identity, data stores, model provider, guardrails, audit, and observability.
5. Key ADRs: knowledge strategy, model provider, vector store, provider abstraction, interaction mode, human-review boundary.
6. Capacity math: users, questions per day, token budget, monthly cost, vector storage, p99 latency budget, scale-up scenario.
7. Failure modes: outage, hallucination, retrieval regression, leakage, cost blowup, stale source data.
8. Hand-off: ADR bundle, capacity sheet, risk register, evaluation plan, backlog, runbook, and launch-readiness checklist.

> One-liner: **a useful AI architecture page is a decision record with a diagram, arithmetic, and named risks.**


Related: [[02 Literature Notes/AI Architecture/AI Solution Architecture — Applied]] · [[04 Code Snippets/AI Architecture/AI Week 19b One Page Architecture Generator]]
