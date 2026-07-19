# Paired Permutation Test

> Domain 6 · Statistical Rigor in Eval. Sign-flip permutation test for paired eval deltas.

```python
import numpy as np

def paired_signflip_pvalue(delta, B=10000, seed=0):
    rng=np.random.RandomState(seed); delta=np.asarray(delta,float); obs=abs(delta.mean())
    null=[abs((delta*rng.choice([-1,1], len(delta))).mean()) for _ in range(B)]
    return (np.sum(np.asarray(null)>=obs)+1)/(B+1)
print(paired_signflip_pvalue([0.1,0.0,0.2,-0.1,0.05]))
```


Related: [[04 Code Snippets/LLM/Bootstrap Confidence Interval]]
