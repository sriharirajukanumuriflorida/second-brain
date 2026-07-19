# LLM Inference Is Usually Memory-Bandwidth Bound

The bottleneck in serving an LLM is typically **moving data** (weights + KV cache) through GPU memory, not raw arithmetic. That reframes optimization: the biggest wins come from making things smaller and reusing work, not from more FLOPs. Hence quantization (fewer bits per weight), KV cache (reuse past K/V), GQA/MQA (smaller KV), and FlashAttention (don't materialize the score matrix) — all memory-side levers.

> One-liner: **you're moving bytes, not doing math** — shrink the weights, shrink and reuse the KV cache, and read less per step.


Related: [[02 Literature Notes/LLM Engineering/LLM Efficiency]] · [[03 Permanent Notes/Attention Is Quadratic in Sequence Length]]
