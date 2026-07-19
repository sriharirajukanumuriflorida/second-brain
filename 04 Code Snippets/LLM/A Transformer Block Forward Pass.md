# A Transformer Block Forward Pass

> Domain 2 · Transformer / LLM Architecture. Pre-norm decoder block: attention + MLP with residuals, in numpy.

```python
import numpy as np
def softmax(x, ax=-1):
    x = x - x.max(ax, keepdims=True); e = np.exp(x); return e / e.sum(ax, keepdims=True)
def layernorm(x, g, b, eps=1e-5):
    mu = x.mean(-1, keepdims=True); var = x.var(-1, keepdims=True)
    return g * (x - mu) / np.sqrt(var + eps) + b
def gelu(x): return 0.5 * x * (1 + np.tanh(0.797885 * (x + 0.044715 * x**3)))

def attn(x, Wqkv, Wo, causal=True):
    seq, d = x.shape
    Q, K, V = (x @ Wqkv).reshape(seq, 3, d).transpose(1, 0, 2)
    s = Q @ K.T / np.sqrt(d)
    if causal: s = np.where(np.triu(np.ones((seq, seq)), 1).astype(bool), -1e9, s)
    return (softmax(s) @ V) @ Wo

def block(x, p):
    x = x + attn(layernorm(x, p['g1'], p['b1']), p['Wqkv'], p['Wo'])
    h = gelu(layernorm(x, p['g2'], p['b2']) @ p['Wup'])
    return x + h @ p['Wdown']

d, seq, ff = 16, 5, 64; rng = np.random.RandomState(0)
p = dict(g1=np.ones(d), b1=np.zeros(d), g2=np.ones(d), b2=np.zeros(d),
         Wqkv=rng.randn(d, 3*d)*.1, Wo=rng.randn(d, d)*.1,
         Wup=rng.randn(d, ff)*.1, Wdown=rng.randn(ff, d)*.1)
x = rng.randn(seq, d)
print("block output:", block(x, p).shape)
```


Related: [[04 Code Snippets/LLM/Counting Transformer Parameters]]
