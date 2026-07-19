# Toy CLIP Cosine Alignment

> Domain 10 · Multimodal AI (VLMs, image/audio embeddings, multimodal RAG). Compute cosine similarity between toy image and text vectors to simulate contrastive alignment.

```python
import numpy as np

def normalize(x):
    x = np.asarray(x, dtype=float)
    return x / (np.linalg.norm(x) + 1e-12)

def cosine(a, b):
    return float(np.dot(normalize(a), normalize(b)))

image_vecs = {"dog_photo": [0.9, 0.1, 0.2], "chart": [0.1, 0.9, 0.3]}
text_vecs = {"a dog running": [0.85, 0.05, 0.25], "a revenue chart": [0.05, 0.95, 0.2]}
for img, iv in image_vecs.items():
    best = max(text_vecs, key=lambda t: cosine(iv, text_vecs[t]))
    print(img, "->", best, round(cosine(iv, text_vecs[best]), 3))
```


Related: [[04 Code Snippets/LLM/Multimodal Retrieval Ranker]]
