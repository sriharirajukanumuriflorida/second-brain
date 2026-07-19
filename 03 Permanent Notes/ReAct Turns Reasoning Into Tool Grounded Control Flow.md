# ReAct Turns Reasoning Into Tool Grounded Control Flow

ReAct alternates Thought, Action, Observation, and Final. It is the core prompt pattern behind many agents because it lets the model reason about what it needs, call a tool, inspect the result, and continue. The power comes from observations that ground the next step in external state.

The failure modes are equally agentic: hallucinated tools, malformed arguments, loops, and overuse. A production ReAct prompt needs a strict tool list, schemas, stop criteria, max iterations, and observation handling rules.

> One-liner: **ReAct is useful when the model must look before it answers.**


Related: [[02 Literature Notes/LLM Engineering/Reasoning Prompt Patterns]] · [[04 Code Snippets/LLM/ReAct Loop With Fake Tools]]
