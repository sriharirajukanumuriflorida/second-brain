# MMR Diversification Selector

> Domain 4 · Advanced Retrieval (hybrid, reranking, MMR). Select relevant but non-redundant chunks for the final RAG context.

```python
import numpy as np

def mmr(query_vec, doc_vecs, doc_ids, k=3, lam=0.7):
    selected, remaining = [], list(range(len(doc_ids)))
    sims_q = doc_vecs @ query_vec
    while remaining and len(selected) < k:
        best_i, best_score = None, -1e9
        for i in remaining:
            redundancy = max([float(doc_vecs[i] @ doc_vecs[j]) for j in selected] or [0.0])
            score = lam * float(sims_q[i]) - (1 - lam) * redundancy
            if score > best_score: best_i, best_score = i, score
        selected.append(best_i); remaining.remove(best_i)
    return [doc_ids[i] for i in selected]

rng = np.random.RandomState(1)
vecs = rng.randn(5, 6); vecs /= np.linalg.norm(vecs, axis=1, keepdims=True)
q = rng.randn(6); q /= np.linalg.norm(q)
print(mmr(q, vecs, [f"d{i}" for i in range(5)]))
```


Related: [[04 Code Snippets/LLM/Reciprocal Rank Fusion Retriever]]
