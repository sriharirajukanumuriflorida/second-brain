# Corrective RAG Is an Evidence Quality Gate

Corrective RAG evaluates retrieved context before generation. Strong evidence proceeds to answering; partial evidence triggers query rewrite; weak evidence broadens sources; no evidence or exhausted budget produces refusal. The point is to avoid blindly giving the LLM low-quality context and hoping the prompt fixes it.

> One-liner: **grade retrieval before generation, or the generator will launder weak evidence into confidence.**


Related: [[02 Literature Notes/LLM Engineering/Agentic RAG]]
