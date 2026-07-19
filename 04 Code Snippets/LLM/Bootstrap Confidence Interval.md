# Bootstrap Confidence Interval

> Domain 6 · Statistical Rigor in Eval. Nonparametric bootstrap CI for an eval metric.

```python
import numpy as np

def bootstrap_ci(x, stat=np.mean, B=5000, alpha=0.05, seed=0):
    rng=np.random.RandomState(seed); x=np.asarray(x,float)
    vals=[stat(rng.choice(x, size=len(x), replace=True)) for _ in range(B)]
    return np.quantile(vals, [alpha/2, 1-alpha/2])
print(bootstrap_ci([1,0,1,1,0,1]))
```


Related: [[02 Literature Notes/LLM Engineering/Statistical Rigor in Eval]]
