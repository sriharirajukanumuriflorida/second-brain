# Retry Backoff With Jitter Simulator

> Domain 8 · Reliability Patterns (retries, fallbacks, circuit breakers). Generate bounded exponential backoff delays without actually sleeping.

```python
import random

def retry_schedule(base=0.2, factor=2.0, cap=3.0, attempts=5, seed=7):
    rng = random.Random(seed)
    delays = []
    for i in range(attempts):
        raw = min(cap, base * (factor ** i))
        jitter = rng.uniform(0, raw * 0.25)
        delays.append(round(raw + jitter, 3))
    return delays

def call_with_retries(outcomes):
    delays = retry_schedule(attempts=len(outcomes))
    for i, ok in enumerate(outcomes):
        if ok: return {"attempt": i+1, "slept_seconds": round(sum(delays[:i]), 3), "status": "ok"}
    return {"attempt": len(outcomes), "slept_seconds": round(sum(delays[:-1]), 3), "status": "failed"}

print(retry_schedule())
print(call_with_retries([False, False, True]))
```


Related: [[04 Code Snippets/LLM/Circuit Breaker State Machine]]
