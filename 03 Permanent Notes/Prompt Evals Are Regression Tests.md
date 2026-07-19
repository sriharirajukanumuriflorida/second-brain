# Prompt Evals Are Regression Tests

A golden prompt eval set is the regression suite for model behavior. It encodes must-not-break cases: common inputs, edge cases, adversarial injections, low-context refusals, prior incidents, and schema constraints. CI should compare candidate prompt/model behavior against the current release before traffic sees it.

For structured tasks, test exact fields, types, labels, and refusal paths. For generative tasks, test properties: groundedness, citation coverage, forbidden claims, length, and cost. Output diffs matter more than prompt-text diffs.

> One-liner: **golden tests turn prompt taste into release gates.**


Related: [[02 Literature Notes/LLM Engineering/Prompt Versioning]] · [[03 Permanent Notes/Prompts Need Semantic Versions]]
