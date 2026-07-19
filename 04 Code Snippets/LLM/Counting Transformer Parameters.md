# Counting Transformer Parameters

> Domain 2 · Transformer / LLM Architecture. Estimate parameter count and the attention/MLP split for any config.

```python
def params(n_layers, d_model, vocab, ff_mult=4):
    attn = 4 * d_model * d_model           # Wq,Wk,Wv,Wo
    mlp  = 2 * ff_mult * d_model * d_model # up + down
    per_layer = attn + mlp
    embed = vocab * d_model                # tied embed/unembed
    total = n_layers * per_layer + embed
    return total, attn / per_layer, mlp / per_layer

for name, (L, d, v) in {"GPT-2 small":(12,768,50257),
                        "GPT-2 XL":(48,1600,50257),
                        "7B-ish":(32,4096,32000)}.items():
    t, a, m = params(L, d, v)
    print(f"{name:<12} ~{t/1e6:>8.1f}M params   attn={a:.0%} mlp={m:.0%} per block")
```


Related: [[04 Code Snippets/LLM/A Transformer Block Forward Pass]]
