# Comparing Embedding Models on a Golden Set

## Purpose
- Score multiple embedding models on YOUR data with a golden set (queries + known-relevant docs), reporting recall@k, MRR, index size, and ingest cost — the evidence behind an embedding-model selection memo.

## Language
- Python

## Snippet
```python
# pip install numpy sentence-transformers   (optional: openai)
import numpy as np

# --- pluggable embedders: return L2-normalized [N, d] arrays ------------------
def st_embedder(model_name):
    from sentence_transformers import SentenceTransformer
    m = SentenceTransformer(model_name)
    def _embed(texts):
        return m.encode(texts, normalize_embeddings=True)
    return _embed

def openai_embedder(model="text-embedding-3-small", dims=None):
    from openai import OpenAI
    client = OpenAI()
    def _embed(texts):
        kw = {"dimensions": dims} if dims else {}
        r = client.embeddings.create(model=model, input=texts, **kw)
        v = np.array([d.embedding for d in r.data])
        return v / np.linalg.norm(v, axis=1, keepdims=True)
    return _embed

# --- evaluation ---------------------------------------------------------------
def evaluate(embed, queries, corpus, gold, k=5):
    C = np.asarray(embed(corpus))
    Q = np.asarray(embed([q for q, _ in queries]))
    hits, rr = 0, []
    for (q, _), qv in zip(queries, Q):
        order = np.argsort(-(C @ qv))[:k]
        rel = gold[q]
        ranks = [r for r, idx in enumerate(order, 1) if idx in rel]
        if ranks: hits += 1; rr.append(1/ranks[0])
        else: rr.append(0.0)
    return {"recall@%d" % k: round(hits/len(queries), 3),
            "MRR": round(float(np.mean(rr)), 3)}

def index_cost(n_chunks, dims, bytes_per_dim=4, avg_tokens=400, price_per_m=0.02):
    return {"index_GB": round(n_chunks*dims*bytes_per_dim/1e9, 2),
            "ingest_USD": round(n_chunks*avg_tokens/1e6*price_per_m, 2)}

if __name__ == "__main__":
    corpus = ["Reset your password from the login page.",
              "Refunds are available within 30 days.",
              "Enable two-factor authentication in settings.",
              "Support hours are 9 to 5, Mon-Fri."]
    queries = [("how do I recover my login?", None),
               ("what is the refund window?", None)]
    gold = {"how do I recover my login?": {0, 2},
            "what is the refund window?": {1}}

    candidates = {
        "MiniLM-L6 (384d, local)": (st_embedder("all-MiniLM-L6-v2"), 384),
        # "openai-3-small (1536d)": (openai_embedder(), 1536),
        # "openai-3-small@256 (Matryoshka)": (openai_embedder(dims=256), 256),
    }
    for name, (embed, dims) in candidates.items():
        q = evaluate(embed, queries, corpus, gold, k=3)
        c = index_cost(2_000_000, dims)
        print(f"{name:32s} {q}  scaled-to-2M: {c}")
```

## Notes
- **The golden set is the deliverable's backbone**: 30–100 real queries with known-relevant docs. Small sets pick winners by noise.
- Rank candidates by **recall@k / MRR on your data**, not by the MTEB average — and report latency + cost alongside quality.
- `index_cost` makes the tradeoff concrete: halving dims (Matryoshka) or f32→int8 (`bytes_per_dim=1`) are direct savings.
- Keep the eval protocol identical across models (same k, same normalization) for a fair comparison.
- Switching models later means re-embedding the whole corpus — choose deliberately.

## Links
- Source note: [[02 Literature Notes/LLM Engineering/Embedding Model Selection]]
- Related: [[04 Code Snippets/LLM/Chunk Size Evaluation Harness]]
