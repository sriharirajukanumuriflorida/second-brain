# Multimodal Retrieval Ranker

> Domain 10 · Multimodal AI (VLMs, image/audio embeddings, multimodal RAG). Fuse text, image, and audio vector scores with modality weights for multimodal RAG.

```python
import numpy as np

def rank_multimodal(query, items, weights=None):
    weights = weights or {"text": 0.5, "image": 0.5, "audio": 0.0}
    q = {k: np.asarray(v, float) for k, v in query.items()}
    scored = []
    for item in items:
        score = 0.0
        for mod, w in weights.items():
            if mod in q and mod in item:
                a = q[mod] / (np.linalg.norm(q[mod]) + 1e-12)
                b = np.asarray(item[mod], float); b = b / (np.linalg.norm(b) + 1e-12)
                score += w * float(np.dot(a, b))
        scored.append((score, item["id"]))
    return sorted(scored, reverse=True)

items = [{"id":"slide_dog", "text":[.8,.1], "image":[.9,.1]},
         {"id":"slide_sales", "text":[.1,.9], "image":[.2,.8]}]
print(rank_multimodal({"text":[.7,.2], "image":[1,.0]}, items))
```


Related: [[04 Code Snippets/LLM/Toy CLIP Cosine Alignment]]
