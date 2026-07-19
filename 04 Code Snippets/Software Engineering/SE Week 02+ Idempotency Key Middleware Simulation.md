# SE Week 02+ Idempotency Key Middleware Simulation

> Week 02+ · Distributed Systems Reality. A Stripe-style idempotency store that deduplicates retries, caches responses, detects parameter mismatch, and expires old entries.

```python
from dataclasses import dataclass
import hashlib, json

@dataclass
class IdempotencyRecord:
    params_hash: str
    status: int
    body: dict
    expires_at: float

class IdempotencyStore:
    def __init__(self, ttl_seconds=86_400):
        self.ttl = ttl_seconds
        self.records = {}
    def _hash(self, payload):
        encoded = json.dumps(payload, sort_keys=True).encode()
        return hashlib.sha256(encoded).hexdigest()
    def handle(self, key, payload, now, handler):
        rec = self.records.get(key)
        params_hash = self._hash(payload)
        if rec and rec.expires_at >= now:
            if rec.params_hash != params_hash:
                return 409, {"error": "idempotency key reused with different parameters"}
            return rec.status, {**rec.body, "cached": True}
        status, body = handler(payload)
        self.records[key] = IdempotencyRecord(params_hash, status, body, now + self.ttl)
        return status, body

def create_charge(payload):
    return 201, {"charge_id": "ch_" + payload["order_id"], "amount": payload["amount"]}

store = IdempotencyStore(ttl_seconds=10)
print(store.handle("k1", {"order_id": "7", "amount": 500}, 0, create_charge))
print(store.handle("k1", {"order_id": "7", "amount": 500}, 1, create_charge))
print(store.handle("k1", {"order_id": "7", "amount": 700}, 2, create_charge))
```


Related: [[03 Permanent Notes/SE Week 02+ Distributed Systems Failure Playbook]]
