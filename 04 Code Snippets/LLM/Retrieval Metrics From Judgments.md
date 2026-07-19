# Retrieval Metrics From Judgments

> Domain 4 · Retrieval Evaluation (recall@k, MRR, NDCG). Compute hit rate, precision@k, recall@k, MRR, and DCG/NDCG from ranked results.

```python
import math

def metrics(ranked, relevant, k=3):
    top = ranked[:k]
    rel_top = [d for d in top if d in relevant]
    hit = 1.0 if rel_top else 0.0
    precision = len(rel_top) / k
    recall = len(rel_top) / max(1, len(relevant))
    rr = next((1/(i+1) for i,d in enumerate(ranked) if d in relevant), 0.0)
    return {"hit":hit, "precision":precision, "recall":recall, "mrr":rr}

print(metrics(["d2","d1","d3"], {"d1","d4"}, k=3))
```


Related: [[04 Code Snippets/LLM/Labeled Retrieval Eval Harness]]
