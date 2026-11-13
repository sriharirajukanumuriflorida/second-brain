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

---

## 9. Interview Q&A

**Q: Write the exact top-k function and explain its complexity.**
A: The simplest, exact version of vector search is called "flat" or "brute force" search: compare your query vector against every single stored vector, one at a time, and keep track of the best matches as you go.

In code, this is just: compute the similarity score (dot product, if everything's normalized) between the query and every vector in your corpus — this gives you one score per stored vector — then sort those scores and take the top k highest ones. There's no cleverness here, no shortcuts — it's genuinely comparing the query against everything you have.

For the complexity: if you have `N` stored vectors, each of dimension `d`, computing one similarity score takes work proportional to `d` (you're doing `d` multiplications and additions for one dot product). Doing this for all `N` vectors costs `N × d` total. So the whole operation is `O(N·d)` — it scales directly with both how many vectors you have and how big each vector is. This is fine, even fast, for tens of thousands of vectors. But at millions of vectors, this becomes genuinely slow for a system answering live queries, which is exactly why approximate methods (ANN) exist — to avoid paying this full `N × d` cost on every single query.

*One-liner: flat search computes the similarity between the query and every stored vector, then picks the top k — this is exact (recall=1.0) but costs `O(N × d)`, scaling with both corpus size and vector dimension, which gets too slow at millions of vectors.*

**Q: When are cosine similarity, dot product, and Euclidean (L2) distance interchangeable, and why?**
A: They become interchangeable under one specific condition: every vector has been normalized to length 1 (L2-normalized).

As covered in the Embeddings topic, cosine similarity is defined as the dot product divided by both vectors' lengths — and once every vector's length is fixed at 1, that division does nothing, so cosine similarity and the plain dot product become mathematically identical. That covers two of the three.

Euclidean distance (straight-line distance between two points) takes a bit more algebra to connect, but it works out to a direct mathematical relationship with cosine similarity too, specifically when vectors are normalized: squared Euclidean distance equals `2 minus 2 times the cosine similarity`. Since that's a fixed, predictable relationship (not an approximation), ranking results by smallest Euclidean distance gives you the *exact same ordering* as ranking by highest cosine similarity — a smaller Euclidean distance always corresponds to a higher cosine similarity, when vectors are normalized. So even though these are three differently-named ways of measuring "distance" or "similarity," for normalized vectors they're really just three different units measuring the same underlying thing, and sorting by any of them gives you the same ranking of results.

The key condition to remember, though, is that this equivalence only holds when vectors are normalized. If you skip normalization, these three metrics can genuinely disagree with each other and give different rankings — so whether you've normalized your vectors isn't a minor implementation detail, it's what determines whether this whole equivalence even applies.

*One-liner: cosine, dot product, and Euclidean distance all become mathematically interchangeable (giving the exact same ranking) once every vector is normalized to length 1 — without that normalization step, they can genuinely disagree and rank results differently.*

**Q: What does recall@k mean for an ANN index, and why do you need a flat baseline to measure it?**
A: Recall@k here is answering a specific question: "of the true, correct top-k matches (the ones you'd get from exhaustively checking every vector), how many did the fast approximate search actually find?" If the true top-5 matches for a query are documents A, B, C, D, E, and your ANN index returns A, B, D, E, and some other document F instead of C, that's a recall@5 of 4 out of 5, or 80%.

Here's why you need a flat (exact, brute-force) baseline to measure this at all: recall@k is defined by comparison against the *true* top-k — and the only way to know what the true top-k actually is, is to compute it exactly, with no approximation. The flat/brute-force search described earlier is exactly this: slow, but guaranteed correct. Without ever running that exact version, at least on a sample of your queries, you have no ground truth to compare your fast ANN index's results against — you'd be flying blind, with no way to know if your "fast" search is returning great results or secretly missing half of the true matches every time.

This is why, in practice, teams keep a flat baseline around even in production systems that use a fast ANN index for real traffic — not to serve live queries with it, but specifically to periodically measure: is our approximate index still finding what it should be finding, or has some setting drifted it into missing real matches without anyone noticing.

*One-liner: recall@k measures how many of the true top-k results (found by exact, brute-force search) an approximate index actually returns — you need a flat baseline specifically because it's the only way to know what the "true" top-k even is, giving you something real to measure your fast index's accuracy against.*

**Q: Contrast pre-filtering and post-filtering — when does each fail?**
A: Both exist to handle the same real-world need: "find similar vectors, but only among the ones matching some condition" (only this user's documents, only from this year, and so on) — they just apply that condition at different points in the process.

Pre-filtering narrows down the candidate set by the metadata condition *first*, then only searches for similarity within that narrowed set. This guarantees you always get exactly as many genuinely matching results as exist, up to k — but it can be slow if the filter is very selective (say, it narrows a million vectors down to just 50) combined with an index structure that isn't built to efficiently search only within an arbitrary subset — in the worst case, this can force something close to a full scan of the filtered subset rather than taking advantage of the ANN index's speed.

Post-filtering does it the other way around: search for similarity across the *entire* corpus first, get the top-k most similar results, and only *then* throw away any that don't match the metadata condition. This is fast, since the ANN search itself runs at full speed with no filtering slowing it down. But here's where it fails: if the metadata condition is selective enough (say, only 1% of documents belong to this particular user), it's entirely possible that none, or very few, of the top-k results from the unfiltered search actually match that condition — so after filtering, you might end up with far fewer than k results, even though plenty of genuinely matching documents exist somewhere deeper in the corpus that the initial top-k search never surfaced.

So the choice depends on how selective your filter is and how important completeness is: narrow, security-critical filters (like per-user access control, where missing a genuinely accessible document is a real problem) lean toward pre-filtering despite the speed cost; broad, permissive filters (like "only show results from the last year" on a mostly-recent corpus) lean toward post-filtering, since it's unlikely to actually exclude much of the top-k anyway.

*One-liner: pre-filtering narrows by metadata before searching (complete, but can be slow for narrow filters), post-filtering searches first and discards non-matches after (fast, but can return fewer than k results if the filter is selective) — narrow or security-critical filters lean pre-filter, broad permissive ones lean post-filter.*

**Q: Give three things a vector database does that a flat numpy index doesn't.**
A: A flat numpy array of vectors can genuinely do similarity search — but it's missing most of what makes a system usable and safe in actual production, not just in a prototype notebook.

First: updates and deletes. Real corpora change — documents get added, edited, or removed over time. A numpy array has no built-in concept of "update this one vector" or "remove this one" without you manually rebuilding indices and tracking what maps to what — a real vector database handles this as a first-class operation (upsert, delete) without you having to rebuild anything from scratch.

Second: persistence and reliability at scale. A numpy array lives in memory and disappears if the process restarts, unless you've built your own saving/loading logic. A vector database handles persisting data to disk, recovering after a crash or restart, and — for larger deployments — sharding data across multiple machines and replicating it for high availability, all without you writing that infrastructure yourself.

Third: metadata filtering and hybrid search, done efficiently. You could bolt a basic metadata filter onto a numpy array, but a real vector database has this built in as an efficient, indexed operation (not a slow linear scan through metadata for every query), and often ships with the ability to combine dense vector search with keyword-based (BM25) search as a unified, tuned capability, rather than you having to stitch two separate systems together yourself.

*One-liner: a vector database handles updates/deletes, persistence/scaling (surviving restarts, sharding, replication), and efficient metadata filtering/hybrid search as built-in, production-ready features — a flat numpy array gives you none of this without you building it yourself from scratch.*

**Q: A client needs per-user document isolation in RAG — how do you implement it in vector search?**
A: The core requirement is: when user A searches, they should only ever see documents they're actually allowed to access — never documents belonging to user B, even if those documents would otherwise be a great semantic match for the query.

The way to implement this is by attaching metadata to every vector at ingestion time — specifically, something like an owner ID, a tenant ID, or an access-control list identifying exactly who's allowed to see this particular chunk. This metadata gets stored alongside the vector itself, not as an afterthought.

Then, at query time, every single search has to include a mandatory filter based on the requesting user's identity — something like "only search among vectors where owner ID equals this specific user's ID" (or their tenant/team, depending on how access is structured). And critically, based on the pre-filter vs post-filter distinction above, this needs to be a *pre-filter*, not a post-filter — because this isn't a "nice to have, mostly correct" scoping like a recency filter, it's a hard security boundary. If you used post-filtering here, a scenario is possible where the top-k unfiltered results are dominated by other users' documents, and after filtering down to just this user's allowed content, you return far fewer results than expected — or worse, if the filtering step has any bug at all, you risk exposing another user's content before the filter even gets a chance to run.

The practical takeaway: access control in RAG isn't something you bolt on in the prompt ("please only discuss documents belonging to this user") — that's not a real security boundary, since the retrieval step already happened before the model saw anything. The actual enforcement has to happen in the vector search itself, as a mandatory pre-filter tied to the user's real identity, before any ranked results are returned at all.

*One-liner: tag every vector with an owner/tenant ID at ingestion, then enforce a mandatory pre-filter on that ID at query time, scoped to the requesting user's real identity — this has to be pre-filtering specifically, since access control is a hard security boundary, not something you can safely apply only after search results have already been computed.*

## 8. Links
- Domain MOC: [[06 Maps of Content/LLM Engineering Concepts]]
- Code: [[04 Code Snippets/LLM/Flat vs FAISS Vector Search]], [[04 Code Snippets/LLM/Filtered Vector Search with Metadata]]
- Distilled: [[03 Permanent Notes/Vector Search Is Approximate Nearest Neighbors at Scale]]
- Upstream: [[02 Literature Notes/LLM Engineering/Embeddings]] · Downstream: [[02 Literature Notes/LLM Engineering/ANN Index Internals]]
