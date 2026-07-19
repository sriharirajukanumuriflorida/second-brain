# A Reusable Prompt Contract Builder

> Domain 3 · Prompt Contracts. Assemble a role-structured message list from a stable contract + runtime input.

```python
from dataclasses import dataclass, field

@dataclass
class PromptContract:
    system: str
    task: str
    schema: str                      # description of required JSON
    examples: list = field(default_factory=list)   # (input, output) pairs
    refusal: str = 'If context is insufficient, return {"answer": null}.'

    def build(self, user_input, context=""):
        msgs = [{"role": "system", "content": self.system}]
        dev = f"TASK:\n{self.task}\n\nOUTPUT SCHEMA:\n{self.schema}\n\nRULES:\n{self.refusal}"
        msgs.append({"role": "system", "content": dev})
        for ex_in, ex_out in self.examples:                 # few-shot
            msgs.append({"role": "user", "content": ex_in})
            msgs.append({"role": "assistant", "content": ex_out})
        content = user_input if not context else (
            f"<context>\n{context}\n</context>\n\nQUESTION: {user_input}")
        msgs.append({"role": "user", "content": content})
        return msgs

c = PromptContract(
    system="You are a precise invoice extractor. Output only JSON.",
    task="Extract vendor and total from the invoice text.",
    schema='{"vendor": string, "total": number}',
    examples=[("Acme, $12", '{"vendor": "Acme", "total": 12}')])
for m in c.build("BobCo billed $99"): print(m["role"], "->", m["content"][:50])
```


Related: [[04 Code Snippets/LLM/Prompt Contract Validation Gate]]
