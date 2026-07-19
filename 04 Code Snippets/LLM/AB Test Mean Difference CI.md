# AB Test Mean Difference CI

> Domain 6 · Online Evaluation (A/B, live feedback). Compute treatment-control lift with a confidence interval.

```python
import math

def mean_ci(control, treatment, z=1.96):
    nc, nt = len(control), len(treatment)
    mc, mt = sum(control)/nc, sum(treatment)/nt
    vc = sum((x-mc)**2 for x in control)/(nc-1)
    vt = sum((x-mt)**2 for x in treatment)/(nt-1)
    se = math.sqrt(vc/nc + vt/nt)
    diff = mt - mc
    return diff, (diff - z*se, diff + z*se)
print(mean_ci([0,1,1,0,1], [1,1,1,0,1]))
```


Related: [[02 Literature Notes/LLM Engineering/Online Evaluation]]
