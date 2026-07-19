# Temperature Top-k Top-p Sampler

> Domain 2 · Decoding & Sampling. A single sampler function covering temperature, top-k and nucleus (top-p).

```python
import numpy as np
def sample_next(logits, temperature=1.0, top_k=0, top_p=0.0, rng=None):
    rng = rng or np.random.RandomState(0)
    logits = logits.astype(float)
    if temperature <= 0:                       # greedy
        return int(logits.argmax())
    logits = logits / temperature
    probs = np.exp(logits - logits.max()); probs /= probs.sum()
    if top_k and top_k < len(probs):           # top-k truncation
        keep = np.argsort(probs)[-top_k:]
        mask = np.zeros_like(probs, bool); mask[keep] = True
        probs = np.where(mask, probs, 0)
    if top_p:                                  # nucleus truncation
        order = np.argsort(probs)[::-1]
        csum = np.cumsum(probs[order])
        cutoff = order[csum <= top_p]
        cutoff = cutoff if len(cutoff) else order[:1]
        mask = np.zeros_like(probs, bool); mask[cutoff] = True
        probs = np.where(mask, probs, 0)
    probs /= probs.sum()
    return int(rng.choice(len(probs), p=probs))

logits = np.array([2.0, 1.0, 0.5, 0.1, -1.0, -3.0])
print("greedy     :", sample_next(logits, temperature=0))
print("T=1.2 top_p:", sample_next(logits, temperature=1.2, top_p=0.9))
```


Related: [[04 Code Snippets/LLM/Temperature Reshapes the Distribution]]
