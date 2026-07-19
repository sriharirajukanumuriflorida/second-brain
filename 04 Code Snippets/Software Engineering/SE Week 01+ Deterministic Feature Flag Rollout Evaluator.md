# SE Week 01+ Deterministic Feature Flag Rollout Evaluator

> Week 01+ · Production Delivery Engineering. A LaunchDarkly-style percentage rollout evaluator using stable SHA-256 buckets, tenant targeting, and kill-switch behavior.

```python
from dataclasses import dataclass, field
import hashlib

@dataclass(frozen=True)
class FeatureFlag:
    key: str
    enabled: bool
    rollout_percent: int = 0
    allow_tenants: set[str] = field(default_factory=set)
    deny_users: set[str] = field(default_factory=set)

def bucket(flag_key, user_id, salt="prod"):
    digest = hashlib.sha256(f"{salt}:{flag_key}:{user_id}".encode()).hexdigest()
    return int(digest[:8], 16) % 100

def evaluate(flag, user_id, tenant_id):
    if not flag.enabled or user_id in flag.deny_users:
        return False
    if tenant_id in flag.allow_tenants:
        return True
    return bucket(flag.key, user_id) < flag.rollout_percent

flag = FeatureFlag("llm_answer_v2", enabled=True, rollout_percent=25, allow_tenants={"acme"})
for user, tenant in [("u1", "acme"), ("u2", "beta"), ("u3", "beta"), ("u4", "beta")]:
    print(user, tenant, bucket(flag.key, user), evaluate(flag, user, tenant))
```


Related: [[03 Permanent Notes/SE Week 01+ Deployment Strategies Decision Guide]]
