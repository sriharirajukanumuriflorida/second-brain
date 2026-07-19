# Vector Store Selection Matrix

> Domain 4 · Vector Database Landscape. Score vector DB candidates against product requirements instead of vendor vibes.

```python
CANDIDATES = {
    "FAISS": {"managed":0, "simple":2, "filters":0, "hybrid":0, "ops":0},
    "Chroma": {"managed":0, "simple":3, "filters":1, "hybrid":1, "ops":1},
    "pgvector": {"managed":1, "simple":2, "filters":3, "hybrid":2, "ops":2},
    "Qdrant": {"managed":2, "simple":2, "filters":3, "hybrid":2, "ops":2},
    "Weaviate": {"managed":2, "simple":2, "filters":2, "hybrid":3, "ops":2},
    "Pinecone": {"managed":3, "simple":2, "filters":2, "hybrid":2, "ops":3},
    "Milvus": {"managed":1, "simple":1, "filters":2, "hybrid":2, "ops":2}}

def choose(weights):
    scores = {name: sum(features.get(k,0)*w for k,w in weights.items()) for name,features in CANDIDATES.items()}
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

print(choose({"managed":3, "filters":2, "hybrid":1, "ops":2})[:3])
```


Related: [[04 Code Snippets/LLM/Local ANN Tradeoff Simulator]]
