# Red Team Risk Coverage Matrix

> Domain 6 · Red-Teaming / Adversarial Eval. Summarize adversarial suite coverage by risk category.

```python
from collections import Counter
def coverage(attacks, required):
    counts = Counter(a["risk"] for a in attacks)
    return {risk: counts.get(risk, 0) for risk in required}
print(coverage([{"risk":"prompt_injection"},{"risk":"harmful_content"}], ["prompt_injection","data_leakage","harmful_content","tool_abuse"]))
```


Related: [[04 Code Snippets/LLM/Adversarial Prompt Suite Runner]]
