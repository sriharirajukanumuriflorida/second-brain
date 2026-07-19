# Continuous Batching Scheduler Simulator

> Domain 8 · Inference & Serving (vLLM, TGI, batching, streaming). Simulate token-step scheduling where new requests enter as completed ones leave.

```python
from collections import deque

def continuous_batch(requests, max_batch=3):
    queue = deque(dict(id=i, remaining=t) for i, t in requests)
    active, timeline, step = [], [], 0
    while queue or active:
        while queue and len(active) < max_batch:
            active.append(queue.popleft())
        timeline.append((step, [r["id"] for r in active]))
        for r in active: r["remaining"] -= 1
        active = [r for r in active if r["remaining"] > 0]
        step += 1
    return timeline

reqs = [("a", 4), ("b", 2), ("c", 6), ("d", 1), ("e", 3)]
for step, batch in continuous_batch(reqs): print(step, batch)
```


Related: [[04 Code Snippets/LLM/SSE Token Streaming Demo]]
