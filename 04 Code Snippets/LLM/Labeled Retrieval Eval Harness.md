# Labeled Retrieval Eval Harness

> Domain 4 · Retrieval Evaluation (recall@k, MRR, NDCG). Run a retriever over a small labeled set and aggregate metrics by query.

```python
def evaluate(cases, retriever, k=3):
    totals = {"hit":0, "precision":0, "recall":0, "mrr":0}
    for q, relevant in cases:
        ranked = retriever(q)
        m = metrics(ranked, relevant, k)
        for key in totals: totals[key] += m[key]
        print(q, ranked[:k], m)
    return {key: val/len(cases) for key, val in totals.items()}

cases = [("refund", {"policy"}), ("shipping", {"ship"})]
def toy(q): return ["policy","faq","ship"] if q == "refund" else ["faq","ship","policy"]
print(evaluate(cases, toy, 3))
```


Related: [[04 Code Snippets/LLM/Retrieval Metrics From Judgments]]
