# Attention Is Quadratic in Sequence Length

The score matrix `QKᵀ` is `[seq, seq]`, so self-attention costs **O(seq²·d)** time and **O(seq²)** memory. Doubling context quadruples the attention compute. This is the root economic fact behind long-context pricing, the push for FlashAttention (which avoids materializing the full matrix), and sparse/linear-attention research.

At inference, the **KV cache** stores past Keys and Values so each new token attends to cached state in O(seq) instead of recomputing O(seq²) — trading memory for speed and making KV cache the dominant inference-memory cost.

> One-liner: **context is quadratic** — every design decision about long documents, chunking, and serving cost traces back to this.


Related: [[02 Literature Notes/LLM Engineering/Attention Deep-Dive]] · [[02 Literature Notes/LLM Engineering/LLM Efficiency]]
