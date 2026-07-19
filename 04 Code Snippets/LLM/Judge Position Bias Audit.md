# Judge Position Bias Audit

> Domain 6 · LLM-as-a-Judge Done Right. Swap answer order and count preference patterns that reveal position sensitivity.

```python
def audit_position_bias(judge, pairs):
    biased = 0
    for a,b in pairs:
        if judge(a,b) == judge(b,a): biased += 1
    return biased / max(1, len(pairs))
def always_a(a,b): return "A"
print(audit_position_bias(always_a, [("x","y"),("better","worse")]))
```


Related: [[04 Code Snippets/LLM/Pairwise Judge Calibration Harness]]
