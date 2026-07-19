# FAISS Is a Library While Vector Databases Are Retrieval Services

FAISS provides high-performance vector indexing/search primitives, but it does not by itself provide a production service: persistence, APIs, metadata filters, tenancy, backups, monitoring, access control, and operational workflows are your responsibility. Vector databases package many of those concerns.

This does not make FAISS worse; it makes it the right tool for embedded indexes, experiments, or teams willing to build the service layer.

> One-liner: **FAISS searches vectors; a vector database operates retrieval.**


Related: [[02 Literature Notes/LLM Engineering/Vector Database Landscape]] · [[02 Literature Notes/LLM Engineering/Vector Search]]
