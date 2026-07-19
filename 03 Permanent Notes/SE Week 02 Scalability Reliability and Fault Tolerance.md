# SE Week 02 Scalability Reliability and Fault Tolerance

**Scalability** is the ability to handle more load, often by reducing work (caching), spreading work (horizontal scaling), partitioning data, or moving slow tasks async. **Reliability** is the probability the system behaves correctly over time. **Fault tolerance** is the ability to keep serving despite component failure.

The primitives interact: timeouts prevent caller exhaustion; retries recover transient faults but need budgets and jitter; circuit breakers stop repeated calls to failing dependencies; bulkheads isolate capacity; idempotency makes replay safe; queues absorb bursts but require lag monitoring and dead-letter handling.

> One-liner: **scale handles more traffic; reliability keeps promises; fault tolerance survives broken parts** — design all three explicitly.


Related: [[02 Literature Notes/Software Engineering/System Design Fundamentals]] · [[04 Code Snippets/Software Engineering/SE Week 02 Token Bucket Rate Limiter]]
