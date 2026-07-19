# Exact and Semantic LLM Cache

> Domain 8 · Cost Architecture (caching, routing, gateway). Combine normalized exact lookup with cosine similarity over toy embeddings.

```python
import numpy as np, re

def norm(text): return re.sub(r"\s+", " ", text.lower()).strip()
def embed(text):
    v = np.zeros(8)
    for ch in norm(text): v[ord(ch) % len(v)] += 1
    return v / (np.linalg.norm(v) + 1e-9)
def cosine(a,b): return float(np.dot(a,b) / ((np.linalg.norm(a)*np.linalg.norm(b)) + 1e-9))

class LLMCache:
    def __init__(self): self.exact, self.semantic = {}, []
    def put(self, prompt, answer):
        self.exact[norm(prompt)] = answer
        self.semantic.append((embed(prompt), answer, prompt))
    def get(self, prompt, threshold=.92):
        key = norm(prompt)
        if key in self.exact: return "exact", self.exact[key]
        scored = [(cosine(embed(prompt), v), ans) for v, ans, _ in self.semantic]
        if scored and max(scored)[0] >= threshold: return "semantic", max(scored)[1]
        return "miss", None

c = LLMCache(); c.put("How do I reset my password?", "Use the reset link.")
print(c.get("how do i reset my password"))
```


Related: [[04 Code Snippets/LLM/Confidence Gated Model Cascade]]
