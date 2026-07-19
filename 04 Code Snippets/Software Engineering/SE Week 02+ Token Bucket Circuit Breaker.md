# SE Week 02+ Token Bucket Circuit Breaker

> Week 02+ · Distributed Systems Reality. A deterministic circuit breaker with closed/open/half-open state plus token-bucket load shedding, using simulated time.

```python
class TokenBucket:
    def __init__(self, capacity, refill_per_second):
        self.capacity = capacity
        self.refill = refill_per_second
        self.tokens = capacity
        self.updated_at = 0.0
    def allow(self, now):
        self.tokens = min(self.capacity, self.tokens + max(0, now - self.updated_at) * self.refill)
        self.updated_at = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

class CircuitBreaker:
    def __init__(self, threshold=2, cooldown=5.0):
        self.threshold = threshold
        self.cooldown = cooldown
        self.failures = 0
        self.state = "closed"
        self.opened_at = None
    def call(self, now, fn):
        if self.state == "open" and now - self.opened_at < self.cooldown:
            return "blocked"
        if self.state == "open":
            self.state = "half-open"
        try:
            result = fn()
            self.failures = 0
            self.state = "closed"
            return result
        except Exception:
            self.failures += 1
            if self.state == "half-open" or self.failures >= self.threshold:
                self.state = "open"
                self.opened_at = now
            return "failed"

bucket = TokenBucket(2, 1)
breaker = CircuitBreaker()
bad = lambda: (_ for _ in ()).throw(TimeoutError())
for t in [0, 0, 0, 1, 2, 8]:
    print(t, "admit", bucket.allow(t), "breaker", breaker.call(t, bad), breaker.state)
```


Related: [[03 Permanent Notes/SE Week 02+ Capacity Estimation Cheat Sheet]]
