# Normalize Embeddings to Use Dot Product as Cosine

## Core Idea
- If every embedding is L2-normalized to unit length, cosine similarity equals the dot product, and Euclidean distance becomes a monotonic function of it. Production systems normalize once at ingestion and then use the cheaper dot product.

## Why It Matters
- Dot product is faster than cosine (no per-comparison magnitude division) and most vector indexes are optimized for it.
- Skipping normalization while using dot product lets vector magnitude leak into scores, artificially favoring longer texts.

## Explanation
- For unit vectors a, b: cos(a,b) = a·b, and ||a−b||² = 2 − 2(a·b), so ranking by dot product, cosine, or Euclidean distance is equivalent.
- Normalize the whole matrix once: v / ||v|| along each row, at ingestion time.
- The same normalization must be applied to query vectors at search time.

## Examples
- `v = v / np.linalg.norm(v, axis=1, keepdims=True)` then `scores = docs @ query`.
- Vector databases expose a metric choice (cosine / dot / L2); with normalized vectors these give the same ranking.

## Links
- Source literature note: [[02 Literature Notes/LLM Engineering/Embeddings]]
- Related notes: [[03 Permanent Notes/Embeddings Turn Meaning into Geometry]]
- Related project:
