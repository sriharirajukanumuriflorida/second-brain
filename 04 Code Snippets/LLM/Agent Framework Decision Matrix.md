# Agent Framework Decision Matrix

> Domain 5 · Agent Framework Literacy. Choose by workflow need

```python
def recommend(needs):
    if needs.get("stateful"): return "LangGraph"
    if needs.get("roles"): return "CrewAI or AutoGen"
    if needs.get("data"): return "LlamaIndex"
    return "raw loop"
print(recommend({"stateful":True}))
```


Related: [[04 Code Snippets/LLM/Portable Agent State Shape]]
