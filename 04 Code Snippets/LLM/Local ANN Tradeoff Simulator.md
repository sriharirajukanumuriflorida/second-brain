# Local ANN Tradeoff Simulator

> Domain 4 · Vector Database Landscape. Simulate recall loss when searching only a candidate subset instead of exact nearest neighbors.

```python
import numpy as np
rng = np.random.RandomState(0)
vecs = rng.randn(200, 16); vecs /= np.linalg.norm(vecs, axis=1, keepdims=True)
q = rng.randn(16); q /= np.linalg.norm(q)
exact = set(np.argsort(vecs @ q)[-10:])

def approx_recall(candidate_fraction):
    n = int(len(vecs) * candidate_fraction)
    candidates = rng.choice(len(vecs), n, replace=False)
    found = set(candidates[np.argsort(vecs[candidates] @ q)[-10:]])
    return len(exact & found) / len(exact)

for frac in [0.1, 0.25, 0.5, 1.0]:
    print(frac, "recall@10", round(approx_recall(frac), 2))
```


Related: [[04 Code Snippets/LLM/Vector Store Selection Matrix]]
