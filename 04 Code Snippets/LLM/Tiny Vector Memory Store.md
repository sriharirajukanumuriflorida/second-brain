# Tiny Vector Memory Store

> Domain 5 · Agent Memory. Deterministic numpy retrieval

```python
import numpy as np
def emb(t):
    v=np.zeros(8)
    for c in t.lower(): v[ord(c)%8]+=1
    return v/(np.linalg.norm(v) or 1)
mem=[("user prefers concise answers",emb("user prefers concise answers"))]
q=emb("preferred style")
print(max((float(q@v),t) for t,v in mem))
```


Related: [[04 Code Snippets/LLM/Safe Memory Write Gate]]
