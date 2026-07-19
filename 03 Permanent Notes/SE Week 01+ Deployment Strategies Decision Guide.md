# SE Week 01+ Deployment Strategies Decision Guide

Deployment strategy is a risk-control choice. Rolling deploys are cheap and fine for stateless services with backward-compatible changes. Blue/green gives fast rollback and clean cutover, but needs duplicate capacity and database compatibility. Canary releases reduce blast radius by sending 1-5% of traffic first, but only work when metrics can detect badness quickly. Feature-flag rollouts control behavior by tenant, user, or cohort after code is deployed.

Database changes need expand/contract migrations regardless of strategy: add nullable columns first, write both only when safe, backfill, switch reads, then remove old fields later.

> One-liner: **deploy bits safely, release behavior deliberately, and always know the rollback path.**


Related: [[02 Literature Notes/Software Engineering/Production Delivery Engineering]] · [[04 Code Snippets/Software Engineering/SE Week 01+ Deterministic Feature Flag Rollout Evaluator]]
