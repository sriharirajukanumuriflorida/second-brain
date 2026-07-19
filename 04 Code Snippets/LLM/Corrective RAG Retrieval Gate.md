# Corrective RAG Retrieval Gate

> Domain 4 · Agentic RAG. Grade retrieved evidence and choose accept, rewrite, broaden, or refuse.

```python
def retrieval_gate(scores, min_top=0.55, min_hits=2):
    strong = [s for s in scores if s >= min_top]
    if len(strong) >= min_hits: return "accept"
    if scores and max(scores) >= min_top: return "rewrite_query"
    if scores: return "broaden_sources"
    return "refuse"

for scores in [[0.8,0.7,0.2], [0.7,0.3], [0.4,0.3], []]:
    print(scores, "->", retrieval_gate(scores))
```


Related: [[04 Code Snippets/LLM/Iterative Retrieval Agent Loop]]
