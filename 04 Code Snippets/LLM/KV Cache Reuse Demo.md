# KV Cache Reuse Demo

> Domain 2 · LLM Efficiency. Show that caching K/V makes per-step attention O(seq) instead of recomputing O(seq²).

```python
import numpy as np
rng = np.random.RandomState(0)
d = 32
def new_kv(tok): return rng.randn(d), rng.randn(d)   # pretend projections

# Without cache: recompute all K,V every step -> O(t^2) work
def no_cache(tokens):
    work = 0
    for t in range(1, len(tokens)+1):
        for _ in range(t): new_kv(0); work += 1     # rebuild 0..t
    return work

# With cache: only the new token's K,V each step -> O(t)
def with_cache(tokens):
    cache, work = [], 0
    for tok in tokens:
        cache.append(new_kv(tok)); work += 1         # append one
    return work

toks = list(range(200))
print("work no-cache :", no_cache(toks))     # ~ n^2/2
print("work with-cache:", with_cache(toks))  # ~ n
print("speedup ~", no_cache(toks)//with_cache(toks), "x at seq=200")
```


Related: [[04 Code Snippets/LLM/KV Cache Memory Estimator]]
