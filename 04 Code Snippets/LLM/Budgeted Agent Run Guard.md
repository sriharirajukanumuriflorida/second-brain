# Budgeted Agent Run Guard

> Domain 5 · Agent Reliability & Cost Control. Enforce step and token caps

```python
class Budget:
    def __init__(self,steps=3,tokens=100): self.steps=steps; self.tokens=tokens; self.s=0; self.t=0
    def charge(self,n):
        self.s+=1; self.t+=n
        if self.s>self.steps or self.t>self.tokens: raise RuntimeError("budget exceeded")
b=Budget(); b.charge(20); print(b.s,b.t)
```


Related: [[04 Code Snippets/LLM/Agent Trace Span Logger]]
