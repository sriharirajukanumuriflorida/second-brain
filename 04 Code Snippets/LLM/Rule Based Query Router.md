# Rule Based Query Router

> Domain 4 · Query Transformation (HyDE, multi-query, routing). Route transformed questions to specialized retrievers with an uncertainty fallback.

```python
ROUTES = {"policy":["refund","compliance","policy"],
          "code":["stacktrace","function","class","api"],
          "metrics":["revenue","count","dashboard","sql"]}

def route(query):
    q = query.lower()
    scores = {name: sum(term in q for term in terms) for name, terms in ROUTES.items()}
    best, score = max(scores.items(), key=lambda x: x[1])
    return best if score else "general"

for q in ["refund policy", "function stacktrace", "monthly revenue", "what is RAG"]:
    print(q, "->", route(q))
```


Related: [[04 Code Snippets/LLM/HyDE and Multi Query Expander]]
