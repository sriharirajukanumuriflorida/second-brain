# SE Week 02 Token Bucket Rate Limiter

> Week 02 · System Design Fundamentals. A deterministic token-bucket limiter with simulated timestamps: burst capacity plus sustained refill rate.

```python
from dataclasses import dataclass

@dataclass
class TokenBucket:
    capacity: float
    refill_per_second: float
    tokens: float = 0.0
    updated_at: float = 0.0

    def __post_init__(self):
        self.tokens = self.capacity

    def allow(self, now, cost=1.0):
        elapsed = max(0.0, now - self.updated_at)
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_per_second)
        self.updated_at = now
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False

bucket = TokenBucket(capacity=3, refill_per_second=1)
for t in [0, 0, 0, 0, 1.0, 1.1, 2.0]:
    print(f"t={t:>3}: allow={bucket.allow(t)} tokens={bucket.tokens:.1f}")
```


Related: [[03 Permanent Notes/SE Week 02 Scalability Reliability and Fault Tolerance]]
