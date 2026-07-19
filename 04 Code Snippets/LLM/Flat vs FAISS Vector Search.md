# Flat vs FAISS Vector Search

## Purpose
- Compare an exact brute-force (flat) search against a FAISS ANN index, and measure the ANN index's recall@k against the exact baseline — the correct way to trust and tune approximate search.

## Language
- Python

## Snippet
```python
# pip install numpy faiss-cpu
import numpy as np

rng = np.random.RandomState(0)
N, d = 50_000, 128
corpus = rng.randn(N, d).astype("float32")
corpus /= np.linalg.norm(corpus, axis=1, keepdims=True)   # normalize
q = corpus[123] + 0.05 * rng.randn(d).astype("float32")
q /= np.linalg.norm(q)

# --- exact baseline (numpy) ---------------------------------------------------
def flat_topk(query, matrix, k=10):
    scores = matrix @ query
    idx = np.argpartition(-scores, k)[:k]
    return idx[np.argsort(-scores[idx])]

exact = set(flat_topk(q, corpus, k=10).tolist())

# --- FAISS ANN index (HNSW) ---------------------------------------------------
import faiss
index = faiss.IndexHNSWFlat(d, 32)          # 32 = graph connectivity (M)
index.hnsw.efConstruction = 80
index.add(corpus)
index.hnsw.efSearch = 64                     # higher efSearch -> better recall, slower
_, ids = index.search(q.reshape(1, -1), 10)
approx = set(ids[0].tolist())

recall = len(exact & approx) / len(exact)
print(f"recall@10 of HNSW vs exact: {recall:.2f}")
print("raise index.hnsw.efSearch to trade latency for recall")
```

## Notes
- **Always keep the flat baseline**: it defines the ground-truth top-k so you can compute the ANN index's recall. Without it you're tuning blind.
- `efSearch` is the recall/latency knob at query time; `M` and `efConstruction` set graph quality at build time.
- Use `IndexFlatIP` for an exact inner-product index (small corpora); `IndexHNSWFlat` or `IndexIVFPQ` for scale.
- Normalize vectors so inner product equals cosine; FAISS `IP` indexes assume you want max inner product.
- For millions of vectors and metadata/updates, prefer a full vector DB (Qdrant/Weaviate/Milvus/pgvector) over raw FAISS.

## Links
- Source note: [[02 Literature Notes/LLM Engineering/Vector Search]]
- Related: [[04 Code Snippets/LLM/Filtered Vector Search with Metadata]]
- Downstream: [[02 Literature Notes/LLM Engineering/ANN Index Internals]]
