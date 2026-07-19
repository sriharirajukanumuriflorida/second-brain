# Eval Framework Selection Matrix

> Domain 6 · Eval Framework Literacy (RAGAS, DeepEval, Promptfoo). Score frameworks against requirements instead of adopting by hype.

```python
frameworks={"RAGAS":{"rag":3,"ci":2,"traces":1},"Promptfoo":{"rag":1,"ci":3,"traces":1},"Langfuse":{"rag":2,"ci":2,"traces":3}}
def rank(needs):
    rows=[]
    for name,caps in frameworks.items(): rows.append((sum(needs.get(k,0)*caps.get(k,0) for k in needs), name))
    return sorted(rows, reverse=True)
print(rank({"rag":3,"ci":2,"traces":1}))
```


Related: [[02 Literature Notes/LLM Engineering/Eval Framework Literacy]]
