# Prompt Registry With Semantic Versions

> Domain 3 · Prompt Versioning & Regression Testing. Store prompts as immutable versioned artifacts with model and eval metadata.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class PromptVersion:
    prompt_id: str
    version: str
    template: str
    model: str
    temperature: float
    schema: str
    eval_set: str
    changelog: str

class PromptRegistry:
    def __init__(self): self._items = {}
    def publish(self, p: PromptVersion):
        key = (p.prompt_id, p.version)
        if key in self._items: raise ValueError(f"already published: {key}")
        self._items[key] = p
    def get(self, prompt_id, version):
        return self._items[(prompt_id, version)]

reg = PromptRegistry()
reg.publish(PromptVersion("support_triage", "1.2.0", "Classify: {ticket}",
                          "fake-model-2026-07", 0.0, "{label,priority}",
                          "triage_gold_v3", "Add billing edge cases"))
print(reg.get("support_triage", "1.2.0"))
```


Related: [[04 Code Snippets/LLM/Golden Prompt Regression Harness]]
