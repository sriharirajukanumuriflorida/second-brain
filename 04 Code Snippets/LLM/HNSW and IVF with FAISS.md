# HNSW and IVF with FAISS

> Domain 1 · ANN Index Internals. Build the three ANN families side by side and measure recall against an exact baseline. `pip install faiss-cpu numpy`.

```python
import faiss, numpy as np

rng = np.random.RandomState(0)
N, d = 100_000, 128
xb = rng.randn(N, d).astype("float32"); xb /= np.linalg.norm(xb, axis=1, keepdims=True)
xq = xb[:1000] + 0.05 * rng.randn(1000, d).astype("float32")
xq /= np.linalg.norm(xq, axis=1, keepdims=True)

# --- exact baseline (ground truth) ---
flat = faiss.IndexFlatIP(d); flat.add(xb)
_, gt = flat.search(xq, 10)

def recall_at_10(ann_ids):
    return np.mean([len(set(a) & set(t)) / 10 for a, t in zip(ann_ids, gt)])

# --- HNSW: navigate a graph ---
hnsw = faiss.IndexHNSWFlat(d, 32)          # M = 32
hnsw.hnsw.efConstruction = 200
hnsw.add(xb)
hnsw.hnsw.efSearch = 64                      # recall/latency dial
_, ids = hnsw.search(xq, 10)
print(f"HNSW  (efSearch=64)  recall@10 = {recall_at_10(ids):.3f}")

# --- IVF: prune with clustering ---
quant = faiss.IndexFlatIP(d)
ivf = faiss.IndexIVFFlat(quant, d, 1024)   # nlist = 1024
ivf.train(xb); ivf.add(xb)
for nprobe in (1, 8, 32):
    ivf.nprobe = nprobe
    _, ids = ivf.search(xq, 10)
    print(f"IVF   (nprobe={nprobe:>2})     recall@10 = {recall_at_10(ids):.3f}")

# --- IVFPQ: prune + compress (m=16 bytes/vector) ---
ivfpq = faiss.IndexIVFPQ(quant, d, 1024, 16, 8)
ivfpq.train(xb); ivfpq.add(xb); ivfpq.nprobe = 32
_, ids = ivfpq.search(xq, 10)
print(f"IVFPQ (nprobe=32)    recall@10 = {recall_at_10(ids):.3f}  (lossy; re-rank for accuracy)")
```

**Point:** HNSW hits high recall out of the box; IVF recall climbs with `nprobe`; IVFPQ trades recall for ~8× memory savings (128·4=512 → 16 bytes). Always measure against the flat baseline.

Related: [[02 Literature Notes/LLM Engineering/ANN Index Internals]] · [[04 Code Snippets/LLM/Tuning ANN Recall vs Latency]]
