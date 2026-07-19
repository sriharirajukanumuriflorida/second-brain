# Set Temperature Zero for Structured and Evaluated Output

For anything that must be *correct and consistent* — JSON tool calls, structured extraction, evaluation runs, retrieval-grounded answers — use **greedy decoding (temperature=0)**. Randomness in these settings only adds schema breaks and non-reproducible evals with no upside. Reserve temperature and nucleus sampling for open-ended content where diversity is the goal.

Caveat: temperature=0 is near-deterministic, not bit-exact — hardware, batching, and floating-point non-associativity can still perturb outputs. For reproducibility, also pin seeds and, where possible, model versions.

> One-liner: **default to temperature=0 for structure/eval, dial up only when you want diversity** — and don't expect perfect determinism.


Related: [[02 Literature Notes/LLM Engineering/Decoding and Sampling]] · [[02 Literature Notes/LLM Engineering/Structured Generation]]
