# Claim Support Overlap Scorer

> Domain 6 · Groundedness / Faithfulness / Hallucination. Deterministic claim-to-context support proxy for groundedness regression tests.

```python
import re

def tokens(s): return set(re.findall(r"[a-z0-9]+", s.lower()))
def claim_support(claim, context):
    c, ctx = tokens(claim), tokens(context)
    return len(c & ctx) / max(1, len(c))
def faithfulness(claims, context, threshold=0.6):
    scores = [claim_support(c, context) for c in claims]
    return {"scores": scores, "faithful": sum(s >= threshold for s in scores) / max(1, len(scores))}
print(faithfulness(["refunds allowed within 30 days", "shipping is free"], "refunds are allowed within 30 days with receipt"))
```


Related: [[02 Literature Notes/LLM Engineering/Groundedness and Faithfulness]]
