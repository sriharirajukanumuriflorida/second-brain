# DPO Loss on Toy Log Probabilities

> Domain 7 · Preference Optimization (RLHF, RLAIF, DPO, ORPO). Compute direct preference optimization loss.

```python
import numpy as np
def dpo_loss(pc,pr,rc,rr,beta=.1):
    z=beta*((pc-pr)-(rc-rr))
    return float(np.logaddexp(0,-z))
print(round(dpo_loss(-8,-9.5,-8.5,-9,.5),3))
```


Related: [[04 Code Snippets/LLM/Preference Pair Quality Checks]]
