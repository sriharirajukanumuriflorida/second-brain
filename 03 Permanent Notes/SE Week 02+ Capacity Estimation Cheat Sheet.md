# SE Week 02+ Capacity Estimation Cheat Sheet

Back-of-envelope math prevents fantasy architectures. Bandwidth: `QPS × payload_size`; 2,000 QPS × 20 KB ≈ 40 MB/s before overhead. Storage: `events/day × bytes/event × retention`; 50M × 2 KB ≈ 100 GB/day raw. Worker count: `arrival_rate × service_time` gives concurrency; 100 QPS × 250 ms needs about 25 busy workers before headroom.

Latency budgets must include auth, database, cache, queue, model/provider calls, serialization, and network. A 300 ms p99 target cannot hide a 500 ms p99 dependency. Add headroom for retries, noisy tenants, batch jobs, and regional failover.

> One-liner: **if the arithmetic does not fit on a napkin, the production system will explain it during an incident.**


Related: [[02 Literature Notes/Software Engineering/Distributed Systems Reality]] · [[04 Code Snippets/Software Engineering/SE Week 02+ Token Bucket Circuit Breaker]]
