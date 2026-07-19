# Vector Search Is Approximate Nearest Neighbors at Scale

## Core Idea
- Vector search returns the top-k stored vectors most similar to a query vector. Exact k-nearest-neighbors (brute force) is simple but O(N·d); production systems use Approximate Nearest Neighbor (ANN) indexes that trade a little recall for large speedups.

## Why It Matters
- This is the retrieval step of RAG — everything upstream exists to populate the index it searches.
- The recall-vs-latency knob is the central operational tradeoff; without an exact baseline you cannot measure or tune an ANN index's recall.

## Explanation
- Similarity uses cosine, dot product (equal to cosine when normalized), or L2 — the metric must match how the embedding model was trained.
- Flat/brute-force search is exact (recall 1.0) and fine up to ~100k vectors or as a correctness baseline; beyond that, ANN indexes (HNSW, IVF, PQ) give sub-linear queries.
- A vector database adds metadata filtering, updates/deletes, persistence, sharding, hybrid search, and quantization on top of raw search.

## Examples
- `scores = matrix @ query; top-k = argsort(-scores)[:k]` is the exact baseline.
- Metadata pre-filtering ("only this user's docs from 2023+") powers access control and recency in enterprise RAG.

## Links
- Source literature note: [[02 Literature Notes/LLM Engineering/Vector Search]]
- Related notes: [[03 Permanent Notes/Embeddings Turn Meaning into Geometry]]
- Related project:
