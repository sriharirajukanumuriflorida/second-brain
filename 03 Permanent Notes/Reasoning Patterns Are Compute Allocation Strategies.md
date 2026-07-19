# Reasoning Patterns Are Compute Allocation Strategies

Reasoning prompt patterns spend extra tokens and calls to improve hard tasks. Chain-of-thought adds intermediate work, ReAct adds tool observations, self-consistency samples multiple solution paths, decomposition splits a problem into subproblems, and reflection revises with feedback. Each pattern is a control-flow choice, not a magic phrase.

Use the cheapest pattern that clears the eval. Direct prompting is best for simple tasks; CoT for multi-step inference; ReAct for external state; self-consistency for brittle high-value decisions; decomposition for long workflows.

> One-liner: **reasoning prompts buy quality with compute — spend it where the task justifies it.**


Related: [[02 Literature Notes/LLM Engineering/Reasoning Prompt Patterns]] · [[02 Literature Notes/LLM Engineering/Prompt Versioning]]
