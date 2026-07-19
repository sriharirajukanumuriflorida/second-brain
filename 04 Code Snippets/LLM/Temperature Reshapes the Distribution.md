# Temperature Reshapes the Distribution

> Domain 2 · Decoding & Sampling. Show numerically how temperature flattens or sharpens the softmax.

```python
import numpy as np
def softmax_T(z, T):
    z = np.array(z, float) / T
    e = np.exp(z - z.max()); return e / e.sum()

logits = [3.0, 2.0, 1.0, 0.0]
for T in (0.25, 0.5, 1.0, 2.0):
    p = softmax_T(logits, T)
    print(f"T={T:>4}  probs={np.round(p,3)}  entropy={-(p*np.log(p)).sum():.2f}")
# low T -> peaked (near one-hot, low entropy); high T -> flat (high entropy)
```


Related: [[04 Code Snippets/LLM/Temperature Top-k Top-p Sampler]]
