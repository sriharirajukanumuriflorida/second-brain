# RAG RBAC Audit Gate

> Domain 9 · AI Security & Governance. Enforce tenant and role boundaries before retrieval and record policy decisions.

```python
from datetime import datetime

class AuditLog:
    def __init__(self):
        self.events = []
    def record(self, user, action, resource, decision, reason):
        self.events.append({
            "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "user": user, "action": action, "resource": resource,
            "decision": decision, "reason": reason,
        })

def can_retrieve(user, doc, log):
    allowed = user["role"] in doc["roles"] and user["tenant"] == doc["tenant"]
    log.record(user["id"], "retrieve", doc["id"], "allow" if allowed else "deny",
               "tenant+role match" if allowed else "RBAC or tenant boundary failed")
    return allowed

log = AuditLog()
user = {"id":"u7", "role":"analyst", "tenant":"acme"}
docs = [{"id":"policy", "roles":{"analyst"}, "tenant":"acme"},
        {"id":"payroll", "roles":{"hr"}, "tenant":"acme"}]
print([d["id"] for d in docs if can_retrieve(user, d, log)])
print(log.events)
```


Related: [[04 Code Snippets/LLM/Deterministic PII Redaction Gate]]
