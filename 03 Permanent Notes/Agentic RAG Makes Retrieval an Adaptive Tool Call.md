# Agentic RAG Makes Retrieval an Adaptive Tool Call

Agentic RAG gives the controller or model the ability to call retrieval repeatedly: plan a subquestion, retrieve, grade the evidence, rewrite or broaden if weak, then answer only when evidence is sufficient. This helps multi-hop and ambiguous tasks that one-shot RAG underserves.

The loop needs strict budgets, logs, and a final citation contract. Without them, adaptivity becomes runaway search.

> One-liner: **let the agent search again, but not forever and not without evidence.**


Related: [[02 Literature Notes/LLM Engineering/Agentic RAG]] · [[02 Literature Notes/LLM Engineering/Query Transformation]]
