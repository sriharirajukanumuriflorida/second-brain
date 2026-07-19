# Offline Mini RAG Pipeline

> Domain 4 · RAG Pipeline Fundamentals. A tiny deterministic RAG pipeline: chunk, embed, retrieve, assemble, and answer from evidence.

```python
import hashlib, numpy as np

def embed(text, dim=32):
    v = np.zeros(dim)
    for tok in text.lower().split():
        h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
        v[h % dim] += 1.0
    return v / (np.linalg.norm(v) + 1e-9)

docs = {"d1":"RAG retrieves external evidence before generation.",
        "d2":"Fine-tuning changes model behavior and style.",
        "d3":"Citations bind generated claims to retrieved chunks."}
index = [(k, text, embed(text)) for k, text in docs.items()]

def retrieve(question, k=2):
    q = embed(question)
    scored = [(float(q @ vec), doc_id, text) for doc_id, text, vec in index]
    return sorted(scored, reverse=True)[:k]

def answer(question):
    hits = retrieve(question)
    evidence = "\n".join(f"[{doc_id}] {text}" for _, doc_id, text in hits)
    return f"Context:\n{evidence}\n\nAnswer: use retrieved evidence and cite chunk ids."

print(answer("Why use citations in RAG?"))
```


Related: [[04 Code Snippets/LLM/Citation Aware Context Assembler]]
