# Generating and Comparing Embeddings

## Purpose
- Generate embeddings (OpenAI API or local offline), L2-normalize them, and compute cosine similarity as a dot product. The foundational building block for all semantic retrieval.

## Language
- Python

## Snippet
```python
# pip install numpy openai      (optional: sentence-transformers for offline)
import os, re, numpy as np

def _local_embed(texts, dim=256):
    "Deterministic hashing embedder so this runs with no API key / offline."
    out = []
    for t in texts:
        v = np.zeros(dim)
        for w in re.findall(r"[a-z0-9]+", t.lower()):
            v[hash(w) % dim] += 1.0
        out.append(v)
    return np.array(out)

def embed(texts, model="text-embedding-3-small", dims=None):
    if os.getenv("OPENAI_API_KEY"):
        from openai import OpenAI
        kw = {"dimensions": dims} if dims else {}
        r = OpenAI().embeddings.create(model=model, input=texts, **kw)
        v = np.array([d.embedding for d in r.data])
    else:
        v = _local_embed(texts)
    # L2-normalize so cosine == dot product
    return v / (np.linalg.norm(v, axis=1, keepdims=True) + 1e-9)

def cosine(a, b):
    return float(a @ b)            # inputs already normalized

if __name__ == "__main__":
    texts = ["car", "automobile", "banana", "how to reset my password"]
    V = embed(texts)
    print("car ~ automobile :", round(cosine(V[0], V[1]), 3))
    print("car ~ banana     :", round(cosine(V[0], V[2]), 3))
    print("car ~ password   :", round(cosine(V[0], V[3]), 3))
```

## Notes
- **Normalize once** at ingestion, then similarity is a single dot product — faster and equal to cosine.
- The `dims` parameter uses Matryoshka truncation on `text-embedding-3` to trade quality for storage/latency.
- Use the **same model + version** for corpus and queries; mixing models puts vectors in different spaces and makes similarity meaningless.
- The local hashing embedder is only for offline demos — it captures lexical overlap, not true semantics (so "car"~"automobile" will look low without an API key).

## Links
- Source note: [[02 Literature Notes/LLM Engineering/Embeddings]]
- Related: [[04 Code Snippets/LLM/Semantic Search Over a Corpus]]
