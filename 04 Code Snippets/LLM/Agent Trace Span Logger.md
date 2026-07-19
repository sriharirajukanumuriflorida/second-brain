# Agent Trace Span Logger

> Domain 5 · Agent Reliability & Cost Control. Record model and tool spans

```python
trace=[]
def span(kind, **kw): trace.append({"kind":kind, **kw})
span("model", tokens=42, cost=0.001)
span("tool", name="search", ok=True)
print(trace)
```


Related: [[04 Code Snippets/LLM/Budgeted Agent Run Guard]]
