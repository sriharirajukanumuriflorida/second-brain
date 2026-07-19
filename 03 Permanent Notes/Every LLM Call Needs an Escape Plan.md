# Every LLM Call Needs an Escape Plan

LLM calls fail in more ways than ordinary API calls: provider rate limits, long-tail latency, malformed JSON, safety refusals, tool errors, retrieval misses, and model drift. Production systems need an explicit escape plan: timeout, retry if transient, fallback if dependency-specific, degrade if the full experience is unavailable, and surface honest uncertainty when correctness cannot be preserved.

Reliability is not hiding failure; it is bounding the blast radius and choosing the safest remaining behavior.

> One-liner: **fail smaller, cheaper, and more honestly** than the default stack would.


Related: [[02 Literature Notes/LLM Engineering/Reliability Patterns]] · [[02 Literature Notes/LLM Engineering/Structured Generation]]
