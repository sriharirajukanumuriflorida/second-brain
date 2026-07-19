# RAG Fine Tuning and Long Context Solve Different Problems

RAG, fine-tuning, and long-context are not interchangeable. **RAG** is for external, changing, private, or citation-required knowledge. **Fine-tuning** is for behavior, style, tool-use habits, schemas, and domain skill that should be internalized. **Long-context** is useful when the relevant working set is small enough to pass whole and retrieval would be a risky lossy filter.

Mature systems combine them: tuned behavior, retrieved evidence, and long-context assembly when the budget allows.

> One-liner: **RAG changes what the model can read; fine-tuning changes how it behaves.**


Related: [[02 Literature Notes/LLM Engineering/RAG Pipeline Fundamentals]] · [[02 Literature Notes/LLM Engineering/Fine Tuning]]
