# Scaled Dot-Product Attention in NumPy

> Domain 2 · Attention Deep-Dive. Self-contained scaled dot-product attention with optional causal mask.

```python
import numpy as np

def softmax(x, axis=-1):
    x = x - x.max(axis=axis, keepdims=True)
    e = np.exp(x)
    return e / e.sum(axis=axis, keepdims=True)

def attention(Q, K, V, causal=False):
    dk = Q.shape[-1]
    scores = Q @ K.swapaxes(-1, -2) / np.sqrt(dk)   # [seq, seq]
    if causal:
        seq = scores.shape[-1]
        mask = np.triu(np.ones((seq, seq)), k=1).astype(bool)
        scores = np.where(mask, -1e9, scores)
    weights = softmax(scores, axis=-1)
    return weights @ V, weights

seq, d = 4, 8
rng = np.random.RandomState(0)
Q = K = V = rng.randn(seq, d)
out, w = attention(Q, K, V, causal=True)
print("output:", out.shape, "  row sums (=1):", w.sum(1).round(3))
```


Related: [[04 Code Snippets/LLM/Multi-Head Attention in NumPy]]
