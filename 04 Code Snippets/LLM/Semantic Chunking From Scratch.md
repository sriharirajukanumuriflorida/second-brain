# Semantic Chunking From Scratch

## Purpose
- Implement semantic chunking without any framework, to own the algorithm behind §2.4(b): sentence-embedding, consecutive cosine distance, percentile breakpoint detection, and buffered smoothing. Use to understand exactly what `SemanticChunker` does.

## Language
- Python

## Snippet
```python
# pip install numpy openai
import re
import numpy as np
from openai import OpenAI

client = OpenAI()

def split_sentences(text):
    # Simple, dependency-free sentence splitter. Swap for spaCy/nltk in prod.
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]

def embed(texts, model="text-embedding-3-small"):
    resp = client.embeddings.create(model=model, input=texts)
    return np.array([d.embedding for d in resp.data])

def cosine_distance(a, b):
    return 1.0 - np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def semantic_chunk(text, percentile=95, buffer=1):
    sentences = split_sentences(text)
    if len(sentences) <= 1:
        return [text]

    # OPTIONAL smoothing: embed each sentence WITH its neighbors (buffer window)
    # so a single odd sentence doesn't create a false boundary.
    windows = [
        " ".join(sentences[max(0, i - buffer): i + buffer + 1])
        for i in range(len(sentences))
    ]
    emb = embed(windows)

    # distances between consecutive sentences  (eq. 2.4b)
    dists = np.array([cosine_distance(emb[i], emb[i + 1])
                      for i in range(len(emb) - 1)])
    threshold = np.percentile(dists, percentile)
    breakpoints = [i + 1 for i, d in enumerate(dists) if d > threshold]

    # group sentences between consecutive breakpoints into chunks
    chunks, start = [], 0
    for bp in breakpoints + [len(sentences)]:
        chunks.append(" ".join(sentences[start:bp]))
        start = bp
    return chunks

if __name__ == "__main__":
    text = open("report.txt").read()
    chunks = semantic_chunk(text, percentile=95)
    print(f"{len(chunks)} semantic chunks")
    for i, c in enumerate(chunks[:3]):
        print(f"\n--- chunk {i} ({len(c)} chars) ---\n{c[:200]}")
```

## Notes
- **This is the whole algorithm**: embed sentences → cosine distance between neighbors → cut where distance exceeds a percentile threshold. Everything else is plumbing.
- `buffer` smooths noise: embedding each sentence together with its neighbors prevents a single stylistic outlier from forcing a false boundary.
- `percentile` is the sensitivity knob: 95 = only the sharpest topic shifts cut (fewer, larger chunks); 80 = more, smaller chunks. Tune with the eval harness, not by eye.
- Cost = one embedding per sentence at ingestion. For large corpora, batch the `embed` calls and consider a cheaper local embedding model.
- Alternative breakpoint methods: standard-deviation (`mean + kσ`) or gradient (largest jumps) instead of percentile.

## Links
- Source note: [[02 Literature Notes/LLM Engineering/Chunking Strategies]]
- Related: [[04 Code Snippets/LLM/Semantic and Contextual Chunking]], [[04 Code Snippets/LLM/Chunk Size Evaluation Harness]]
