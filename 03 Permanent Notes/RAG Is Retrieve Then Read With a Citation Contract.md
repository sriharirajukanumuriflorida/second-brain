# RAG Is Retrieve Then Read With a Citation Contract

Retrieval-augmented generation is best understood as **retrieve then read**: first find a small evidence set from an external corpus, then ask the LLM to answer under a contract that requires citations and allows refusal. The knowledge lives in documents and indexes, not only in weights, so it can be updated, filtered, deleted, and audited.

The contract matters: answer only from provided context, cite stable chunk IDs for factual claims, and return an insufficient-context response when evidence is missing.

> One-liner: **RAG makes the model an open-book reader, but only citations make the reading auditable.**


Related: [[02 Literature Notes/LLM Engineering/RAG Pipeline Fundamentals]] · [[03 Permanent Notes/Always Give the Model a Refusal Path]]
