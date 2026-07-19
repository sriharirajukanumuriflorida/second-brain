# RAG Authorization Happens Before Retrieval

A RAG system must not retrieve documents a user is not allowed to see. Once unauthorized text enters the prompt, the breach has already happened; asking the model to ignore it is not access control. Apply tenant, role, document ACL, region, and time-bound entitlement filters before vector ranking or at least before context assembly.

Audit both allowed and denied retrieval decisions so security teams can reconstruct incidents and prove controls operated.

> One-liner: **never put forbidden context in front of the model** — authorization is a retriever responsibility, not a model behavior.


Related: [[02 Literature Notes/LLM Engineering/AI Security and Governance]] · [[02 Literature Notes/LLM Engineering/RAG Evaluation]]
