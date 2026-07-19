# Reciprocal Rank Fusion Retriever

> Domain 4 · Advanced Retrieval (hybrid, reranking, MMR). Merge dense and lexical ranked lists without score calibration.

```python
def rrf(*ranked_lists, k=60):
    scores = {}
    for ranked in ranked_lists:
        for rank, doc_id in enumerate(ranked, 1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

dense = ["refund_policy", "returns_faq", "shipping"]
bm25 = ["sku_ABC123", "refund_policy", "returns_faq"]
print(rrf(dense, bm25)[:4])
```


Related: [[04 Code Snippets/LLM/MMR Diversification Selector]]
