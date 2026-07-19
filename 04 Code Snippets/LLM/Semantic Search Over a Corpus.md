# Semantic Search Over a Corpus

## Purpose
- End-to-end minimal semantic search: embed a corpus, embed a query, rank by cosine (dot product), return top-k. The nucleus of every RAG retriever, with no vector database required.

## Language
- Python

## Snippet
```python
# pip install numpy openai
import os, re, numpy as np

def embed(texts, model="text-embedding-3-small"):
    if os.getenv("OPENAI_API_KEY"):
        from openai import OpenAI
        r = OpenAI().embeddings.create(model=model, input=texts)
        v = np.array([d.embedding for d in r.data])
    else:  # offline fallback
        dim = 256; v = []
        for t in texts:
            x = np.zeros(dim)
            for w in re.findall(r"[a-z0-9]+", t.lower()):
                x[hash(w) % dim] += 1.0
            v.append(x)
        v = np.array(v)
    return v / (np.linalg.norm(v, axis=1, keepdims=True) + 1e-9)

class SemanticIndex:
    def __init__(self, docs):
        self.docs = docs
        self.vectors = embed(docs)          # [N, d], normalized
    def search(self, query, k=3):
        q = embed([query])[0]               # [d], normalized
        scores = self.vectors @ q           # [N] dot products = cosine
        top = np.argsort(-scores)[:k]
        return [(self.docs[i], round(float(scores[i]), 3)) for i in top]

if __name__ == "__main__":
    corpus = [
        "To reset your password, click 'Forgot password' on the login page.",
        "Our return policy allows refunds within 30 days of purchase.",
        "Enable two-factor authentication in Security settings.",
        "Business hours are 9am to 5pm, Monday through Friday.",
    ]
    idx = SemanticIndex(corpus)
    for doc, score in idx.search("how do I recover my login?", k=2):
        print(f"{score:>5}  {doc}")
```

## Notes
- This is exactly what a vector database does at scale — brute-force here is fine up to ~10k–100k vectors; beyond that use an ANN index (HNSW/IVF) for sub-linear search.
- `self.vectors @ q` computes all similarities in one matrix-vector product; `argsort(-scores)[:k]` is top-k.
- Swap the ranking to hybrid (add BM25 scores) to also catch exact-term queries like error codes.
- Store document metadata alongside vectors to enable filtering and citations in a real system.

## Links
- Source note: [[02 Literature Notes/LLM Engineering/Embeddings]]
- Related: [[04 Code Snippets/LLM/Generating and Comparing Embeddings]]
- Downstream: [[02 Literature Notes/LLM Engineering/Vector Search]]
