# Vector Search

> Topic package — Domain 1 (Data Representation) · Roadmap Weeks 09/14.
> Depth goal: understand what vector search is, exact vs approximate, the distance metrics, metadata filtering, and how a vector database actually serves a query.

## Source
- Track: LLM Engineering (self-directed, FDE roadmap)
- Slide deck: `07 Resources Library/LLM Engineering/Slides/Lesson_05_Vector_Search.pptx`
- Hands-on notebook: `07 Resources Library/LLM Engineering/Notebooks/05_Vector_Search.ipynb` (runs offline)
- Reference reading: Pinecone "What is a Vector Database"; FAISS docs/wiki; Weaviate/Qdrant/Chroma docs; Johnson et al. "Billion-scale similarity search with GPUs" (FAISS, arXiv:1702.08734)
- Builds on: [[02 Literature Notes/LLM Engineering/Embeddings]]
- Date: 2026-07-18

---

## 1. Mental Model

**Vector search answers "which stored vectors are most similar to this query vector?"** Given a query embedding, it returns the top-k nearest neighbors from a corpus of embeddings. That is the retrieval `R` in RAG — everything upstream (ingest, chunk, embed) exists to populate the index this searches.

The naive way — compare the query against **every** stored vector (brute force / flat) — is exact but `O(N·d)` per query. At millions of vectors that's too slow, so production systems use **Approximate Nearest Neighbor (ANN)** indexes that trade a little recall for orders-of-magnitude speedup (covered in depth in the next topic).

A **vector database** wraps all of this: it stores vectors + metadata, builds/maintains an ANN index, supports **filtered** search (metadata predicates), handles updates/deletes, persistence, sharding, and concurrency. Chroma, Qdrant, Weaviate, Pinecone, Milvus, pgvector are the common choices.

> Key intuition: **vector search = k-nearest-neighbors at scale.** Exact kNN is simple but slow; the entire field is about approximating it fast while keeping recall high — and about combining it with metadata filters and keyword search so results are both relevant and correct.

---

## 2. How It Actually Works

### 2.1 Distance metrics (must match how you embedded)
- **Cosine** — angle; the default for text embeddings.
- **Dot product (inner product)** — equals cosine when vectors are normalized; fastest.
- **Euclidean (L2)** — straight-line distance; monotonically related to cosine for unit vectors.

The metric must match the embedding model's training. Mismatched metric = silently worse ranking. With L2-normalized vectors, cosine ≈ dot ≈ (a function of) L2 — so most systems normalize and use dot/cosine.

$$\text{score}(\mathbf{q}, \mathbf{v}) = \mathbf{q} \cdot \mathbf{v} \quad (\text{normalized}), \qquad \text{top-}k = \operatorname*{arg\,top-k}_{v \in \text{corpus}} \text{score}(\mathbf{q}, \mathbf{v})$$

### 2.2 Exact vs approximate
- **Flat / brute force** — compute all N similarities, sort, take k. Exact (recall = 1.0), simple, but `O(N·d)`. Fine up to ~10k–100k vectors, or as a correctness baseline.
- **ANN indexes** — HNSW (graph), IVF (clustering), PQ (compression), and hybrids. Sub-linear query time at the cost of occasionally missing a true neighbor. Governed by a **recall vs latency** knob. (Details: next topic.)

**Recall@k** here means: of the true top-k (by brute force), how many did the ANN index return? This is the number you tune indexes against.

### 2.3 Metadata filtering (the enterprise essential)
Real queries aren't just "similar" — they're "similar **and** allowed / recent / from this source." Vector DBs attach metadata to each vector and support filters:
- **Pre-filter**: restrict candidates by metadata *then* search (accurate, can be slow if filter is selective vs the index).
- **Post-filter**: search then drop non-matching results (fast, but may return < k after filtering).
Filtering powers **access control** (only this user's docs), recency, and source scoping — non-negotiable in enterprise RAG, and tied to the metadata you attached during chunking.

### 2.4 What the database does for you
Beyond search: **upserts/deletes** (corpora change), **persistence** (survive restarts), **sharding/replication** (scale + HA), **hybrid search** (dense + BM25 fusion), **quantization** (int8/binary to shrink the index), and **consistency** during concurrent writes. Rolling your own with a flat numpy index ignores all of this — fine for a prototype, not for production.

### 2.5 The query lifecycle
1. Embed the query with the *same* model as the corpus.
2. (Optional) apply metadata pre-filter.
3. ANN search the index for top-k candidates.
4. (Optional) rerank / hybrid-fuse with BM25.
5. Return chunks + metadata for prompt assembly and citation.

---

## 3. Implementation

Assumed stack (pin): `numpy` (flat baseline), `faiss-cpu>=1.8` or `chromadb>=0.5` (real index). Snippets:
- [[04 Code Snippets/LLM/Flat vs FAISS Vector Search]]
- [[04 Code Snippets/LLM/Filtered Vector Search with Metadata]]

### 3.1 Exact baseline (numpy) — always keep one to measure recall against
```python
import numpy as np
def flat_topk(query, matrix, k=5):        # matrix: [N, d] normalized
    scores = matrix @ query               # dot product == cosine
    idx = np.argpartition(-scores, k)[:k]
    return idx[np.argsort(-scores[idx])]  # top-k, sorted
```

### 3.2 Real ANN index (FAISS)
```python
import faiss, numpy as np
d = 768
index = faiss.IndexFlatIP(d)              # exact inner-product baseline
# For scale, swap to HNSW:
# index = faiss.IndexHNSWFlat(d, 32); index.hnsw.efSearch = 64
index.add(corpus_matrix.astype('float32'))
scores, ids = index.search(query.reshape(1, -1).astype('float32'), k=5)
```

### 3.3 A vector database (Chroma) with metadata filter
```python
import chromadb
client = chromadb.Client()
col = client.create_collection("docs")     # cosine by default
col.add(ids=ids, embeddings=vectors, documents=texts, metadatas=metas)
col.query(query_embeddings=[qvec], n_results=5,
          where={"source": "handbook", "year": {"$gte": 2023}})
```

---

## 4. Design Decisions & Tradeoffs

| Decision | Guidance |
|---|---|
| **Flat vs ANN** | Flat under ~100k vectors or when you need exact recall; ANN beyond that. |
| **Metric** | Normalize + dot/cosine for text embeddings; match the model's training. |
| **Library vs database** | FAISS (library, you manage persistence/filters) vs Qdrant/Weaviate/Pinecone/Chroma (full DB: metadata, updates, HA). |
| **Pre vs post filter** | Pre-filter for selective, security-critical filters; post-filter for cheap, permissive ones. |
| **Managed vs self-host** | Pinecone (managed, zero-ops) vs Qdrant/Milvus/pgvector (self-host, control/cost). pgvector if you already run Postgres and scale is modest. |
| **Hybrid** | Add BM25 fusion when exact terms (codes/names) matter — dense alone misses them. |

---

## 5. Failure Modes & Gotchas

- **Metric mismatch** (L2 index on unnormalized cosine-trained vectors) → subtly wrong ranking, no error.
- **Forgetting to normalize** before a dot-product index → magnitude skews results.
- **Post-filtering returning < k** → over-selective filter after search leaves too few results; use pre-filter or over-fetch.
- **No exact baseline** → you can't measure your ANN index's recall, so you can't tune it.
- **Rebuilding the index on every write** → some indexes need training/rebuild; understand your DB's update semantics.
- **Ignoring deletes/updates** → stale vectors for edited/removed docs pollute results; wire deletion into your ingestion.
- **Treating recall as free** → aggressive ANN speed settings quietly drop true neighbors; monitor recall@k.
- **Query embedded with a different model/prefix than corpus** → garbage results (ties to Embeddings).

---

## 6. FDE Angle

- Vector search is where "the RAG isn't finding things" gets diagnosed: check metric, normalization, filter logic, and ANN recall in that order.
- **Filtering = the access-control story.** Enterprises need per-user/per-tenant scoping; be ready to design pre-filtered search and the metadata schema behind it.
- **Managed vs self-host** is a cost/ops/privacy decision a client will push on — know pgvector (cheap, familiar) vs Pinecone (zero-ops) vs Qdrant/Weaviate (self-host, feature-rich).
- Deliverable: a retrieval service with a **flat baseline for recall measurement**, metadata filtering, and a documented metric/index choice.

---

## 7. Self-Check

1. Write the exact top-k function and explain its complexity.
2. When are cosine, dot product, and L2 interchangeable, and why?
3. What does recall@k mean for an ANN index, and why do you need a flat baseline?
4. Contrast pre-filtering and post-filtering; when does each fail?
5. Give three things a vector database does that a flat numpy index doesn't.
6. A client needs per-user document isolation in RAG — how do you implement it in vector search?

## 8. Links
- Domain MOC: [[06 Maps of Content/LLM Engineering Concepts]]
- Code: [[04 Code Snippets/LLM/Flat vs FAISS Vector Search]], [[04 Code Snippets/LLM/Filtered Vector Search with Metadata]]
- Distilled: [[03 Permanent Notes/Vector Search Is Approximate Nearest Neighbors at Scale]]
- Upstream: [[02 Literature Notes/LLM Engineering/Embeddings]] · Downstream: [[02 Literature Notes/LLM Engineering/ANN Index Internals]]
