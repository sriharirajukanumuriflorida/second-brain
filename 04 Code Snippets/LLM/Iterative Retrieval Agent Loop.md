# Iterative Retrieval Agent Loop

> Domain 4 · Agentic RAG. A small retrieve-grade-rewrite loop with max tool-call budget and cited final answer.

```python
DOCS = {"rag":"RAG retrieves evidence before answering.",
        "hyde":"HyDE rewrites a query into a hypothetical document for retrieval.",
        "crag":"CRAG evaluates retrieval quality and corrects weak searches."}

def retrieve(q):
    q = q.lower()
    return [(k, v) for k, v in DOCS.items() if any(w in v.lower() for w in q.split())]

def agent(question, max_calls=3):
    query = question
    for step in range(max_calls):
        hits = retrieve(query)
        if len(hits) >= 2:
            cites = " ".join(f"[{k}]" for k, _ in hits)
            return f"Answer using evidence {cites}"
        query = query + " RAG retrieval correction"
    return "insufficient_context"

print(agent("How does CRAG improve RAG?"))
```


Related: [[04 Code Snippets/LLM/Corrective RAG Retrieval Gate]]
