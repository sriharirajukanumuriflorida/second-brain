# SE Week 04 Dataclass API Contract Handler

> Week 04 · APIs, Integration & Backend Engineering. A FastAPI-like handler without a server: validate request dicts, enforce auth, and return a response contract.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class CreateTicketRequest:
    title: str
    priority: int

@dataclass(frozen=True)
class TicketResponse:
    id: int
    title: str
    status: str

def parse_create_ticket(payload):
    title = payload.get("title")
    priority = payload.get("priority")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("title must be a non-empty string")
    if not isinstance(priority, int) or not 1 <= priority <= 5:
        raise ValueError("priority must be an integer 1..5")
    return CreateTicketRequest(title=title.strip(), priority=priority)

def require_scope(token, scope):
    scopes = set(token.get("scopes", []))
    if scope not in scopes:
        raise PermissionError(f"missing scope: {scope}")

def create_ticket_handler(payload, token):
    require_scope(token, "tickets:write")
    req = parse_create_ticket(payload)
    return TicketResponse(id=1, title=req.title, status="open")

print(create_ticket_handler({"title": "Latency spike", "priority": 2}, {"sub": "u1", "scopes": ["tickets:write"]}))
```


Related: [[03 Permanent Notes/SE Week 04 REST API Design Checklist]]
