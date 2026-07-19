# Golden Dataset Metric Harness

> Domain 6 · Eval Fundamentals. Minimal reference-based harness with precision, recall, F1, and slice labels.

```python
import numpy as np

def precision_recall_f1(pred, gold):
    pred, gold = set(pred), set(gold)
    tp = len(pred & gold)
    precision = tp / max(1, len(pred))
    recall = tp / max(1, len(gold))
    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    return precision, recall, f1

def evaluate(rows):
    out = []
    for r in rows:
        p, rec, f1 = precision_recall_f1(r["pred_labels"], r["gold_labels"])
        out.append({"id": r["id"], "slice": r["slice"], "precision": p, "recall": rec, "f1": f1})
    return out

rows = [{"id":"a","slice":"easy","pred_labels":["refund"],"gold_labels":["refund"]},
        {"id":"b","slice":"hard","pred_labels":["refund"],"gold_labels":["escalate"]}]
print(evaluate(rows))
```


Related: [[02 Literature Notes/LLM Engineering/Eval Fundamentals]]
