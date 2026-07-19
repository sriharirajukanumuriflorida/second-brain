# Choose LLM Frameworks by the Hard Part of the System

The best framework depends on what is actually hard. If the hard part is simple provider calls, use raw SDKs. If it is integrations, LangChain helps. If it is ingestion, indexing, and retrieval, LlamaIndex or Haystack fit. If it is stateful multi-step workflows, LangGraph fits. If it is prompt behavior optimized against examples, DSPy fits.

> One-liner: **pick the abstraction that matches the bottleneck, not the hype cycle**.


Related: [[02 Literature Notes/LLM Engineering/Framework Ecosystem Literacy]]
