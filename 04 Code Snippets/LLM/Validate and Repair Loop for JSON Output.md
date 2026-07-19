# Validate and Repair Loop for JSON Output

> Domain 2 · Structured / Constrained Generation. Provider-agnostic: parse into a Pydantic model, repair on failure, bounded retries.

```python
import json
from dataclasses import dataclass

# stand-in for pydantic to keep this runnable anywhere
@dataclass
class Invoice:
    vendor: str
    total: float
    line_items: list

def validate(raw: str) -> Invoice:
    data = json.loads(raw)                     # raises on bad JSON
    assert isinstance(data["vendor"], str)
    assert isinstance(data["total"], (int, float))
    assert isinstance(data["line_items"], list)
    # semantic check a schema can't express:
    assert data["total"] >= 0, "total must be non-negative"
    return Invoice(**data)

def generate_structured(call_model, prompt, max_retries=3):
    err = None
    for attempt in range(max_retries):
        msg = prompt if err is None else (
            f"{prompt}\n\nYour previous output was invalid: {err}\n"
            "Return ONLY corrected JSON.")
        raw = call_model(msg)                  # your LLM call (temperature=0)
        try:
            return validate(raw)
        except Exception as e:
            err = str(e)
    raise ValueError(f"failed after {max_retries} attempts: {err}")
```


Related: [[04 Code Snippets/LLM/Constrained Decoding with a Token Mask]]
