# Circuit Breaker State Machine

> Domain 8 · Reliability Patterns (retries, fallbacks, circuit breakers). Open after repeated failures, block calls, then probe with half-open recovery.

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=3, reset_after=2):
        self.threshold = failure_threshold; self.reset_after = reset_after
        self.failures = 0; self.state = "closed"; self.opened_at = None
    def allow(self, tick):
        if self.state == "open" and tick - self.opened_at >= self.reset_after:
            self.state = "half_open"; return True
        return self.state != "open"
    def record(self, ok, tick):
        if ok:
            self.failures = 0; self.state = "closed"; self.opened_at = None
        else:
            self.failures += 1
            if self.failures >= self.threshold:
                self.state = "open"; self.opened_at = tick

cb = CircuitBreaker()
for tick, ok in enumerate([False, False, False, True, True, False]):
    print(tick, "allow", cb.allow(tick), "state", cb.state)
    if cb.allow(tick): cb.record(ok, tick)
```


Related: [[04 Code Snippets/LLM/Retry Backoff With Jitter Simulator]]
