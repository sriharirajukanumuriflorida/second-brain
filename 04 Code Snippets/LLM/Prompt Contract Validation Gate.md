# Prompt Contract Validation Gate

> Domain 3 · Prompt Contracts. Every model response passes through schema validation; failures trigger repair.

```python
import json

def gate(response: str, required: dict):
    # required: {field: type}; enforces the output half of the contract
    data = json.loads(response)
    for field, typ in required.items():
        if field not in data:
            raise ValueError(f"missing field: {field}")
        if data[field] is not None and not isinstance(data[field], typ):
            raise ValueError(f"{field} must be {typ.__name__}")
    return data

REQUIRED = {"vendor": str, "total": (int, float)}
print(gate('{"vendor": "Acme", "total": 12}', REQUIRED))     # ok
try:
    gate('{"vendor": "Acme"}', REQUIRED)                       # missing total
except ValueError as e:
    print("rejected:", e)
```


Related: [[04 Code Snippets/LLM/A Reusable Prompt Contract Builder]]
