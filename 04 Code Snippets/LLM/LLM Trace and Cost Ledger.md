# LLM Trace and Cost Ledger

> Domain 8 · Observability & Monitoring. Record nested spans with tokens, latency, errors, and estimated cost.

```python
from dataclasses import dataclass, field
from time import perf_counter

PRICES = {"small": (0.15, 0.60), "strong": (2.50, 10.00)}

@dataclass
class Span:
    name: str
    attrs: dict = field(default_factory=dict)
    children: list = field(default_factory=list)
    start: float = field(default_factory=perf_counter)
    end: float | None = None
    def finish(self, **attrs):
        self.end = perf_counter(); self.attrs.update(attrs); return self
    @property
    def ms(self): return round(((self.end or perf_counter()) - self.start) * 1000, 2)

def cost(model, input_tokens, output_tokens):
    pin, pout = PRICES[model]
    return (input_tokens * pin + output_tokens * pout) / 1_000_000

root = Span("request", {"trace_id": "t-001"})
llm = Span("llm.call", {"model": "small", "prompt_version": "support-v3"})
root.children.append(llm)
llm.finish(input_tokens=820, output_tokens=140, cost_usd=cost("small", 820, 140), status="ok")
root.finish(status="ok")
print(llm.attrs, "latency_ms=", llm.ms)
```


Related: [[04 Code Snippets/LLM/PII Safe LLM Metrics Dashboard]]
