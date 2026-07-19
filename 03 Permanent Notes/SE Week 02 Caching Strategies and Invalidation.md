# SE Week 02 Caching Strategies and Invalidation

Caching trades freshness and complexity for lower latency and backend load. Common patterns: **cache-aside** (app loads on miss), **read-through** (cache knows loader), **write-through** (write cache and store together), **write-behind** (fast writes, eventual persistence), and **precompute/warm** for known hot keys.

Every cache needs decisions: key shape, TTL, explicit invalidation, eviction policy, acceptable staleness, stampede protection, authorization boundaries, and observability for hit rate and stale responses. A cache with no invalidation story is a correctness bug waiting to become fast.

> One-liner: **cache only what you can afford to be wrong about, and define how it becomes right again.**


Related: [[02 Literature Notes/Software Engineering/System Design Fundamentals]] · [[04 Code Snippets/Software Engineering/SE Week 02 In-Memory LRU Cache]]
