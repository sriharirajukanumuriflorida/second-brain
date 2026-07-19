# Confidence Gated Model Cascade

> Domain 8 · Cost Architecture (caching, routing, gateway). Try a cheap model first and escalate to a strong model only when confidence is low.

```python
def cheap_model(task):
    easy = any(w in task.lower() for w in ["classify", "summarize", "extract"])
    return {"model": "cheap", "answer": "draft answer", "confidence": 0.82 if easy else 0.41, "cost": 0.001}

def strong_model(task):
    return {"model": "strong", "answer": "higher confidence answer", "confidence": 0.93, "cost": 0.02}

def cascade(task, threshold=0.75):
    first = cheap_model(task)
    if first["confidence"] >= threshold:
        return first | {"route": "cheap_only"}
    second = strong_model(task)
    second["cost"] += first["cost"]
    return second | {"route": "escalated"}

for task in ["classify ticket sentiment", "solve a multi-step legal reasoning problem"]:
    print(task, "->", cascade(task))
```


Related: [[04 Code Snippets/LLM/Exact and Semantic LLM Cache]]
