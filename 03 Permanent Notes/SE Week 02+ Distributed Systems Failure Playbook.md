# SE Week 02+ Distributed Systems Failure Playbook

Production distributed-system incidents usually start with one of a few patterns: duplicate requests, delayed messages, lost events from dual writes, retry amplification, stale or stampeding caches, split-brain leaders, poison messages, or missing compensation in a saga.

First response checklist: identify the user-visible invariant, stop amplification with circuit breakers or load shedding, preserve evidence, disable risky flags, drain or pause consumers if needed, replay only idempotent work, and repair state with audited scripts. Long-term fixes are usually idempotency keys, transactional outbox, bounded retries with jitter, DLQs, fencing tokens, and explicit consistency contracts.

> One-liner: **make replay safe before you need replay, and make overload boring before it becomes an outage.**


Related: [[02 Literature Notes/Software Engineering/Distributed Systems Reality]] · [[04 Code Snippets/Software Engineering/SE Week 02+ Idempotency Key Middleware Simulation]]
