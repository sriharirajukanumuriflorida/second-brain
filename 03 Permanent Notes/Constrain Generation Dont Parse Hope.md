# Constrain Generation Dont Parse Hope

To make LLM output trustworthy for downstream code, **enforce a schema instead of parsing free text**. Three levels: prompt-and-validate (weakest), provider structured mode / function calling (strong, easy, provider-specific), and constrained decoding (masks illegal tokens per a grammar so only valid strings are reachable — 100% structural validity, even from small models).

Define the schema once (Pydantic/JSON Schema) and reuse it for the prompt, the constraint, and post-hoc validation. Always add a validate-and-repair fallback for semantic errors that structure can't catch.

> One-liner: **a schema + an enforcement mechanism + a repair loop** turns an LLM into an API you can build on.


Related: [[02 Literature Notes/LLM Engineering/Structured Generation]] · [[02 Literature Notes/LLM Engineering/Prompt Contracts]]
