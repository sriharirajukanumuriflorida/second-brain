# Filtered Vector Search with Metadata

## Purpose
- Combine similarity search with metadata filters (access control, recency, source scoping) — the enterprise-essential pattern. Shows pre-filter vs post-filter and a Chroma example.

## Language
- Python

## Snippet
```python
# pip install numpy   (chromadb optional for the DB example)
import numpy as np

# corpus of (vector, metadata) — vectors normalized
rng = np.random.RandomState(0)
docs = [
    {"text": "Q1 board minutes",   "vec": None, "tenant": "acme", "year": 2024},
    {"text": "Q4 board minutes",   "vec": None, "tenant": "acme", "year": 2022},
    {"text": "Competitor memo",    "vec": None, "tenant": "globex","year": 2024},
    {"text": "HR handbook",        "vec": None, "tenant": "acme", "year": 2023},
]
for didx, dcm in enumerate(docs):
    v = rng.randn(64); dcm["vec"] = v / np.linalg.norm(v)
qv = docs[0]["vec"] + 0.1 * rng.randn(64); qv /= np.linalg.norm(qv)

def search(query, docs, k=3, where=None):
    def keep(m):
        return all(m.get(f) == v if not isinstance(v, dict)
                   else all(op(m.get(f), t) for op, t in _ops(v))
                   for f, v in (where or {}).items())
    # PRE-FILTER: restrict candidates by metadata, THEN rank by similarity
    cand = [d for d in docs if keep(d)]
    scored = sorted(cand, key=lambda d: -float(d["vec"] @ query))
    return [(d["text"], round(float(d["vec"] @ query), 3)) for d in scored[:k]]

def _ops(spec):   # supports {"$gte": 2023} style
    import operator
    m = {"$gte": operator.ge, "$gt": operator.gt, "$lte": operator.le, "$lt": operator.lt}
    return [(m[o], t) for o, t in spec.items()]

# Only Acme's docs from 2023+ are even eligible (tenant isolation + recency)
print(search(qv, docs, k=3, where={"tenant": "acme", "year": {"$gte": 2023}}))
```

```python
# --- The same idea in a real vector DB (Chroma) ---
# import chromadb
# col = chromadb.Client().create_collection("docs")       # cosine by default
# col.add(ids=ids, embeddings=vectors, documents=texts, metadatas=metas)
# col.query(query_embeddings=[qvec], n_results=5,
#           where={"tenant": "acme", "year": {"$gte": 2023}})
```

## Notes
- **Pre-filter** (filter then search) is correct for security-critical, selective filters like tenant isolation — a user must never see another tenant's vectors.
- **Post-filter** (search then drop) is cheaper but can return fewer than k results; over-fetch to compensate.
- Metadata comes from the chunking stage — design the schema (tenant, source, section, date, ACL) up front; retrofitting means re-indexing.
- Filtering is how you implement access control, recency, and source scoping in enterprise RAG.

## Links
- Source note: [[02 Literature Notes/LLM Engineering/Vector Search]]
- Related: [[04 Code Snippets/LLM/Flat vs FAISS Vector Search]]
