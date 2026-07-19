# Assistant Only Cross Entropy

> Domain 7 · Supervised Fine-Tuning & Instruction Tuning. Compute loss only on assistant positions.

```python
import numpy as np
def masked_ce(log_probs, labels, mask):
    idx = np.array(mask, dtype=bool)
    return float((-log_probs[np.arange(len(labels))[idx], np.array(labels)[idx]]).mean())
log_probs = np.log(np.array([[.7,.3],[.4,.6],[.2,.8]]))
print(round(masked_ce(log_probs, [0,1,1], [False, True, True]), 3))
```


Related: [[04 Code Snippets/LLM/Chat Template and Assistant Loss Mask]]
