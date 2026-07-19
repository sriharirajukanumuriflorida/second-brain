# LLM Serving Is Queueing Plus KV Cache Management

Once an LLM is loaded, serving performance depends less on the model name and more on scheduling and memory pressure. Prefill builds KV cache from prompts; decode generates token-by-token while carrying that cache. Continuous batching keeps GPUs busy by adding/removing requests at token boundaries, while vLLM-style paged KV management reduces fragmentation under variable sequence lengths.

Capacity planning must include prompt lengths, output lengths, concurrency, KV bytes, queue wait, time-to-first-token, and p95 latency.

> One-liner: **the scheduler and KV cache are the serving system** — not just the model weights.


Related: [[02 Literature Notes/LLM Engineering/Inference and Serving]] · [[02 Literature Notes/LLM Engineering/LLM Efficiency]]
