# Safe Memory Write Gate

> Domain 5 · Agent Memory. Block secrets and low-value memories

```python
def should_write(text):
    low=text.lower()
    if any(s in low for s in ["password","token","ssn"]): return False
    return any(w in low for w in ["prefers","remember","project"])
print([should_write(x) for x in ["prefers tables","password abc","joke"]])
```


Related: [[04 Code Snippets/LLM/Tiny Vector Memory Store]]
