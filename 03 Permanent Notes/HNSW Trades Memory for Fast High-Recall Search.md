# HNSW Trades Memory for Fast, High-Recall Search

HNSW (Hierarchical Navigable Small World) is a **multi-layer graph** you *navigate* rather than scan. The bottom layer holds every vector; higher layers are sparse random subsets acting like a skip list's express lanes. Search starts at the top, greedily hops to the neighbor nearest the query, and drops a layer when it can't get closer — roughly `O(log N)` hops instead of `O(N)`.

Three knobs:
- **`M`** — edges per node. Higher = better recall, more memory.
- **`efConstruction`** — build-time candidate breadth. Higher = better graph, slower build.
- **`efSearch`** — query-time candidate breadth. **The live recall/latency dial.**

HNSW gives the best recall-at-latency of the ANN families, but stores the full vectors **plus** the graph — so it is the most memory-hungry. It's the default in most vector DBs (Pinecone, Qdrant, Weaviate, Milvus) for corpora under ~10M vectors because it hits high recall with almost no tuning: just raise `efSearch` until recall plateaus.

> One-liner: **HNSW spends RAM to buy speed and recall** — navigate a skip-list-like graph, dial recall with `efSearch`.

Related: [[02 Literature Notes/LLM Engineering/ANN Index Internals]] · [[03 Permanent Notes/IVF and PQ Prune and Compress the Search Space]] · [[03 Permanent Notes/Vector Search Is Approximate Nearest Neighbors at Scale]]
