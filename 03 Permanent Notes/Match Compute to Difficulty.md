# Match Compute to Difficulty

Reasoning and extra sampling only pay off on genuinely hard queries; on easy/factual ones they add cost and can even hurt. The production pattern is **difficulty-aware routing**: estimate how hard a query is (heuristics, a small classifier, or model confidence) and send the easy majority to a cheap one-shot path while reserving expensive reasoning (long CoT, self-consistency, o1-style models) for the hard minority.

This keeps average cost/latency low while capturing the accuracy gains where they matter — and it's directly measurable (accuracy and cost per bucket).

> One-liner: **cheap for easy, reasoning for hard** — route by difficulty instead of paying to think on every call.


Related: [[02 Literature Notes/LLM Engineering/Reasoning Models]] · [[02 Literature Notes/LLM Engineering/Cost Architecture]]
