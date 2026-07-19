# Context Assembly Is Part of the Program

An LLM call is not just a prompt; it is an assembled context window containing instructions, task input, history, retrieval, tools, examples, schemas, and selected memory. The assembly policy determines what the model can use, what it ignores, and what conflicts it must resolve.

Context engineering treats that assembly as production logic: rank candidates, filter irrelevant chunks, compress carefully, enforce token budgets, order critical evidence deliberately, and trace exactly what was included.

> One-liner: **the model reasons over the context you build, so building context is software engineering.**


Related: [[02 Literature Notes/LLM Engineering/Context Engineering]] · [[02 Literature Notes/LLM Engineering/Reasoning Prompt Patterns]]
