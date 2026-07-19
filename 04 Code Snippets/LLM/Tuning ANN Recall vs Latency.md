# Tuning ANN Recall vs Latency

> Domain 1 · ANN Index Internals. Sweep the query-time dial (`efSearch` / `nprobe`) and plot the recall-vs-latency curve so you can justify an operating point. `pip install faiss-cpu numpy`.

```python
import faiss, numpy as np, time

rng = np.random.RandomState(0)
N, d = 100_000, 128
xb = rng.randn(N, d).astype("float32"); xb /= np.linalg.norm(xb, axis=1, keepdims=True)
xq = xb[:2000] + 0.05 * rng.randn(2000, d).astype("float32")
xq /= np.linalg.norm(xq, axis=1, keepdims=True)

flat = faiss.IndexFlatIP(d); flat.add(xb)
_, gt = flat.search(xq, 10)
recall = lambda ids: np.mean([len(set(a) & set(t)) / 10 for a, t in zip(ids, gt)])

hnsw = faiss.IndexHNSWFlat(d, 32); hnsw.hnsw.efConstruction = 200; hnsw.add(xb)

print(f"{'efSearch':>8} {'recall@10':>10} {'ms/query':>9}")
for ef in (8, 16, 32, 64, 128, 256):
    hnsw.hnsw.efSearch = ef
    t0 = time.perf_counter()
    _, ids = hnsw.search(xq, 10)
    ms = (time.perf_counter() - t0) / len(xq) * 1000
    print(f"{ef:>8} {recall(ids):>10.3f} {ms:>9.3f}")
```

Typical output shows recall rising fast then **plateauing** while latency keeps climbing — pick the smallest `efSearch` past the knee. The same pattern holds for IVF's `nprobe`.

**Rules:**
- Tune the *query-time* dial, not the build. Never compare indexes at different recall — compare **latency at equal recall**.
- Stop raising the dial once recall@k plateaus; extra latency buys nothing.
- If PQ is in the index, add an exact re-rank of the top-N candidates before reporting recall.

Related: [[02 Literature Notes/LLM Engineering/ANN Index Internals]] · [[04 Code Snippets/LLM/HNSW and IVF with FAISS]]
