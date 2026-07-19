# Multi-Head Attention in NumPy

> Domain 2 · Attention Deep-Dive. Splits d_model into h heads, attends per head, concatenates and projects.

```python
import numpy as np
from numpy import ndarray

def softmax(x, axis=-1):
    x = x - x.max(axis=axis, keepdims=True); e = np.exp(x)
    return e / e.sum(axis=axis, keepdims=True)

def mha(X, Wq, Wk, Wv, Wo, h, causal=True):
    seq, d = X.shape; dk = d // h
    Q, K, V = X @ Wq, X @ Wk, X @ Wv
    def split(t): return t.reshape(seq, h, dk).transpose(1, 0, 2)  # [h, seq, dk]
    Q, K, V = split(Q), split(K), split(V)
    scores = Q @ K.transpose(0, 2, 1) / np.sqrt(dk)               # [h, seq, seq]
    if causal:
        m = np.triu(np.ones((seq, seq)), 1).astype(bool)
        scores = np.where(m, -1e9, scores)
    ctx = softmax(scores, -1) @ V                                  # [h, seq, dk]
    ctx = ctx.transpose(1, 0, 2).reshape(seq, d)                  # concat heads
    return ctx @ Wo

rng = np.random.RandomState(0); seq, d, h = 5, 16, 4
X = rng.randn(seq, d)
Wq, Wk, Wv, Wo = (rng.randn(d, d) * 0.1 for _ in range(4))
print("MHA output:", mha(X, Wq, Wk, Wv, Wo, h).shape)
```


Related: [[04 Code Snippets/LLM/Scaled Dot-Product Attention in NumPy]]
