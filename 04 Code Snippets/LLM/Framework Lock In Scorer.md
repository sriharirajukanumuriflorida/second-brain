# Framework Lock In Scorer

> Domain 11 · Framework / Ecosystem Literacy (LangChain vs LlamaIndex vs LangGraph vs DSPy). Quantify abstraction tradeoffs using simple weighted criteria for velocity, control, and lock-in.

```python
FRAMEWORK_RISK = {
    "Raw SDK": {"lock_in": 1, "velocity": 2, "control": 5},
    "LangChain": {"lock_in": 3, "velocity": 5, "control": 3},
    "LlamaIndex": {"lock_in": 3, "velocity": 4, "control": 3},
    "LangGraph": {"lock_in": 2, "velocity": 3, "control": 4},
    "DSPy": {"lock_in": 4, "velocity": 3, "control": 4},
}

def score_stack(name, priorities):
    risk = FRAMEWORK_RISK[name]
    return sum(priorities[k] * risk[k] for k in priorities)

priorities = {"velocity": 2, "control": 1, "lock_in": -1}
print(sorted((score_stack(n, priorities), n) for n in FRAMEWORK_RISK)[::-1])
```


Related: [[04 Code Snippets/LLM/LLM Framework Selection Function]]
