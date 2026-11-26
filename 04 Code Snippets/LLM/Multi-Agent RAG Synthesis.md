# Multi-Agent RAG Synthesis

> Domain 4 · Agentic RAG. Independent retrieval agents per source; a synthesis step flags conflicts rather than silently picking one.

```python
def retrieval_agent(source, query):
    FAKE_SOURCES = {
        "docs": "The API rate limit is 100 req/min.",
        "tickets": "Customer reported rate limit as 50 req/min after a recent change.",
    }
    return {"source": source, "evidence": FAKE_SOURCES.get(source, ""), "query": query}

def synthesize(results):
    nonempty = [r for r in results if r["evidence"]]
    if len(nonempty) >= 2 and nonempty[0]["evidence"] != nonempty[1]["evidence"]:
        return {"status": "conflict", "evidence": nonempty}
    if nonempty:
        return {"status": "answer", "evidence": nonempty}
    return {"status": "refuse"}

results = [retrieval_agent(s, "rate limit") for s in ["docs", "tickets"]]
print(synthesize(results))
```

Related: [[04 Code Snippets/LLM/Iterative Retrieval Agent Loop]], [[04 Code Snippets/LLM/Corrective RAG Retrieval Gate]]
