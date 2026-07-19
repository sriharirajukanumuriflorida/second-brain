# Pairwise Judge Calibration Harness

> Domain 6 · LLM-as-a-Judge Done Right. Compare deterministic simulated judge preferences against human labels.

```python
def simulated_judge(a, b):
    keys = {"supported", "specific", "safe", "concise"}
    sa = sum(k in a.lower() for k in keys); sb = sum(k in b.lower() for k in keys)
    return "A" if sa >= sb else "B"
def accuracy(preds, labels): return sum(p == y for p,y in zip(preds, labels)) / len(labels)
pairs = [("specific supported answer", "vague answer"), ("long unsafe answer", "concise safe answer")]
print(accuracy([simulated_judge(a,b) for a,b in pairs], ["A","B"]))
```


Related: [[02 Literature Notes/LLM Engineering/LLM as a Judge]]
