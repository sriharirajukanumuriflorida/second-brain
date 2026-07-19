# IVF and PQ Prune and Compress the Search Space

Two ANN ideas that attack different costs, often combined as `IVFPQ`:

**IVF (Inverted File) — prune.** Cluster the corpus with k-means into `nlist` centroids. Each vector joins its nearest centroid's list. At query time, scan only the `nprobe` lists whose centroids are closest to the query.
- `nlist ≈ √N`…`4√N`; needs a `train()` pass on representative data.
- `nprobe` is the recall/latency dial: `1` = fast but misses neighbors sitting just across a Voronoi boundary; `nprobe = nlist` = exact.
- Memory-light (vectors + a tiny centroid table).

**PQ (Product Quantization) — compress.** Split each vector into `m` sub-vectors, k-means each sub-space (256 centroids = 1 byte). A vector becomes `m` bytes; distances use a query→centroid lookup table (no decompression). `m=64, nbits=8` shrinks a 768-d float32 vector from 3072 → 64 bytes (~48×). It's **lossy**, so pair it with an exact **re-rank** of the top candidates.

> One-liner: **IVF prunes which vectors to look at; PQ shrinks each vector so millions fit in RAM.** `IVFPQ` does both for billion-scale on one machine — at the price of training and re-ranking.

Related: [[02 Literature Notes/LLM Engineering/ANN Index Internals]] · [[03 Permanent Notes/HNSW Trades Memory for Fast High-Recall Search]]
