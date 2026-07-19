# PII Safe LLM Metrics Dashboard

> Domain 8 · Observability & Monitoring. Compute p50/p95 latency, token usage, cost, and redact sensitive fields before logging.

```python
import re, numpy as np
EMAIL = re.compile(r"[\w.%-]+@[\w.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"\d{3}[-.]?\d{3}[-.]?\d{4}")
def redact(text): return PHONE.sub("<PHONE>", EMAIL.sub("<EMAIL>", text))
def summarize(events):
    lat = np.array([e["latency_ms"] for e in events])
    toks = np.array([e["input_tokens"] + e["output_tokens"] for e in events])
    return {"n": len(events), "p50_ms": float(np.percentile(lat, 50)),
            "p95_ms": float(np.percentile(lat, 95)), "error_rate": sum(e["status"] != "ok" for e in events)/len(events),
            "avg_tokens": float(toks.mean()), "total_cost": round(sum(e["cost_usd"] for e in events), 4)}
events = [{"latency_ms": x, "input_tokens": 400+x, "output_tokens": 80, "cost_usd": .001+x/1e7, "status": "ok"} for x in [120,150,180,260,510]]
print(redact("Email me at sri@example.com or 555-123-9999"))
print(summarize(events))
```


Related: [[04 Code Snippets/LLM/LLM Trace and Cost Ledger]]
