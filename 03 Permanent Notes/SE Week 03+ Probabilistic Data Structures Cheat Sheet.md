# SE Week 03+ Probabilistic Data Structures Cheat Sheet

Probabilistic structures trade exactness for fixed memory and predictable speed.

- **Bloom filter**: membership, no false negatives, tunable false positives `p ≈ (1-e^{-kn/m})^k`; great for avoiding negative disk/object-store reads.
- **Counting Bloom**: counters instead of bits, supports deletes, costs more memory and counter overflow care.
- **Cuckoo filter**: membership plus deletes with fingerprint buckets; often practical for high load factors.
- **Count-Min Sketch**: frequency estimates with one-sided overcount; use for heavy hitters, abuse signals, and cache admission.
- **HyperLogLog**: cardinality estimate with fixed memory; relative error about `1.04/sqrt(m)` registers.

Never use approximate membership as a security source of truth. Always publish the error budget and measure it against sampled exact data.

> One-liner: **sketches are memory budgets with math attached.**


Related: [[02 Literature Notes/Software Engineering/Data Structures, Algorithms & Complexity]] · [[04 Code Snippets/Software Engineering/SE Week 03+ Bloom Filter False Positive Demo]]
