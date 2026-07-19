# RAG Quality Is Capped by Ingestion Quality

A retriever can only search what ingestion preserved. If a parser shuffles reading order, drops headings, flattens tables, loses page numbers, or treats OCR errors as truth, the embedding index contains distorted knowledge. The LLM then sees bad context and appears to hallucinate.

Production ingestion should preserve structure: reading order, sections, tables, captions, page provenance, OCR confidence, and parser version. Evaluate ingestion with sample documents and retrieval questions before blaming the model.

> One-liner: **bad parsing becomes bad retrieval, which becomes bad generation**.


Related: [[02 Literature Notes/LLM Engineering/Document Ingestion and Parsing]] · [[02 Literature Notes/LLM Engineering/Chunking Strategies]]
