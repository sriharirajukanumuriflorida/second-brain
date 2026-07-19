# Streaming Improves Trust Before It Improves Throughput

Token streaming via SSE or websockets often does not reduce total generation time, but it dramatically improves perceived responsiveness. Users care about time-to-first-token because it proves the system is working. Streaming also enables cancellation, partial rendering, and progressive UX patterns.

Measure TTFT separately from total latency; a system can have good average latency but terrible first-token delay under batching pressure.

> One-liner: **streaming buys user trust and cancellation control** even when total tokens/sec is unchanged.


Related: [[02 Literature Notes/LLM Engineering/Inference and Serving]] · [[03 Permanent Notes/Quantization and GQA Are the Cheapest Serving Wins]]
