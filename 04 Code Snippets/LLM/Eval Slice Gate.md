# Eval Slice Gate

> Domain 6 · Eval Fundamentals. Convert eval results into an explicit shipping decision with slice thresholds.

```python
from collections import defaultdict

def gate(results, metric="f1", min_overall=0.80, min_slice=0.70):
    overall = sum(r[metric] for r in results) / len(results)
    buckets = defaultdict(list)
    for r in results: buckets[r["slice"]].append(r[metric])
    slices = {k: sum(v)/len(v) for k, v in buckets.items()}
    failures = []
    if overall < min_overall: failures.append(f"overall {overall:.2f} < {min_overall:.2f}")
    failures += [f"slice {k} {v:.2f} < {min_slice:.2f}" for k, v in slices.items() if v < min_slice]
    return {"overall": overall, "slices": slices, "pass": not failures, "failures": failures}

print(gate([{"slice":"easy","f1":1.0},{"slice":"hard","f1":0.5}], min_overall=0.7))
```


Related: [[04 Code Snippets/LLM/Golden Dataset Metric Harness]]
