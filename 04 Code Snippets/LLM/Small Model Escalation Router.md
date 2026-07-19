# Small Model Escalation Router

> Domain 7 · Distillation & Small-Model Strategies. Route uncertain small-model predictions to a larger teacher.

```python
def route(confidence, risk):
    if risk=="high" or confidence < .72: return "teacher"
    return "student"
for c,r in [(0.9,"low"),(0.6,"low"),(0.8,"high")]: print(c,r,route(c,r))
```


Related: [[04 Code Snippets/LLM/Distillation KL Between Toy Distributions]]
