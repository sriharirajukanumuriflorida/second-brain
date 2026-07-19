# KV Cache Memory Estimator

> Domain 2 · LLM Efficiency. Estimate KV-cache size and compare to model weights for a given config.

```python
def kv_cache_gb(n_layers, d_model, seq, batch=1, bytes_per=2, kv_heads=None, n_heads=None):
    # GQA: KV scales with kv_heads/n_heads instead of full d_model
    frac = 1.0 if not (kv_heads and n_heads) else kv_heads / n_heads
    dims = d_model * frac
    total = 2 * n_layers * seq * dims * bytes_per * batch   # 2 = K and V
    return total / 1e9

def weights_gb(n_layers, d_model, vocab, bytes_per=2):
    per = 12 * d_model * d_model
    return (n_layers * per + vocab * d_model) * bytes_per / 1e9

L, d, v = 32, 4096, 32000
print(f"weights (fp16): {weights_gb(L,d,v):.1f} GB")
for seq in (2048, 8192, 32768):
    full = kv_cache_gb(L, d, seq, batch=8)
    gqa  = kv_cache_gb(L, d, seq, batch=8, kv_heads=8, n_heads=32)
    print(f"seq={seq:>6} batch=8  KV(MHA)={full:5.1f}GB  KV(GQA 8/32)={gqa:5.1f}GB")
```


Related: [[04 Code Snippets/LLM/KV Cache Reuse Demo]]
