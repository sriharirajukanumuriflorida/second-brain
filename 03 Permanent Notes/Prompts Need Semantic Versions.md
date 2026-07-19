# Prompts Need Semantic Versions

Production prompts are release artifacts. Use semantic versions to communicate intended behavioral compatibility: patch for wording-only fixes, minor for compatible improvements, major for schema/task/refusal/tool-contract changes. The version should travel with the prompt id, model id, decoding parameters, output schema, examples, owner, changelog, and eval set.

The goal is not pretending prompts are deterministic code; the goal is operational clarity. When a regression appears, you need to know exactly which prompt+model combination produced it and how to roll back.

> One-liner: **if a prompt can break production, it needs a version and a changelog.**


Related: [[02 Literature Notes/LLM Engineering/Prompt Versioning]] · [[02 Literature Notes/LLM Engineering/Prompt Contracts]]
