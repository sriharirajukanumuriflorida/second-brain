# Routing Is Retrieval Source Selection Not Answering

A query router chooses where to search: policy docs, code, tickets, SQL, graph, archive, or broad fallback. It should expose confidence and avoid over-committing to one source when the question is ambiguous.

The route is not the answer; it is a control decision in the retrieval plan. Good systems log route choice, candidate sources, and fallback behavior.

> One-liner: **route the search, not the truth.**


Related: [[02 Literature Notes/LLM Engineering/Query Transformation]]
