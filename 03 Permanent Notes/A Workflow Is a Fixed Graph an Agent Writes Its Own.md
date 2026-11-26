# A Workflow Is a Fixed Graph an Agent Writes Its Own

**In a workflow, your code decides the control flow and the LLM only fills in content at each node; in an agent, the LLM decides the control flow itself, step by step.** Default to the simplest fixed-topology workflow that fits the task's shape — escalate to open-ended agentic control only when the task's path genuinely can't be predicted in advance.

> One-liner: workflows are easier to test and bound because their shape is known ahead of time — pick one of the five canonical shapes (chaining, routing, parallelization, evaluator-optimizer, orchestrator-workers) before reaching for a full agent loop.

Related: [[02 Literature Notes/LLM Engineering/Agentic Workflow Patterns]] · [[02 Literature Notes/LLM Engineering/Agent Loops and Planning]] · [[02 Literature Notes/LLM Engineering/Multi-Agent Orchestration]]
