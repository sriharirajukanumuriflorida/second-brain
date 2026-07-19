# SE Week 03+ B-Tree vs LSM-Tree Decision Guide

Use a **B-tree** when ordered reads, point lookups, range scans, and predictable read latency dominate. B-trees update pages in place, have high fanout, and map well to database indexes such as Postgres. Watch for page splits and random write amplification.

Use an **LSM-tree** when write throughput and append-friendly ingestion dominate. Writes land in memory and immutable sorted files; compaction reorganizes later. This buys write speed but creates read amplification, write amplification during compaction, tombstone complexity, and tail-latency risk.

Decision questions: read/write ratio, range-query needs, data retention, compaction window, storage budget, and p99 SLA.

> One-liner: **B-trees pay writes now for reads later; LSMs defer write pain into compaction and reads.**


Related: [[02 Literature Notes/Software Engineering/Data Structures, Algorithms & Complexity]] · [[04 Code Snippets/Software Engineering/SE Week 03+ Heap Top K Vector Retriever]]
