# Structural Validity Is Not Semantic Correctness

Constrained decoding and JSON mode guarantee the output *parses* against a schema — they say nothing about whether the *values* are right. A perfectly-formed invoice can have a `total` that doesn't equal the sum of `line_items`, an out-of-range date, or an invented vendor. Keep explicit semantic checks (ranges, enums, cross-field consistency, groundedness against source) in code, and feed failures back through a bounded repair loop.

> One-liner: **valid JSON ≠ correct JSON** — enforce structure with grammars, enforce meaning with your own validators and evals.


Related: [[02 Literature Notes/LLM Engineering/Structured Generation]] · [[02 Literature Notes/LLM Engineering/Groundedness and Faithfulness]]
