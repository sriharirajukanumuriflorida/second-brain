# CLIP Similarity Is Retrieval Not Visual Truth

CLIP-style models align images and text in a shared embedding space, enabling text-to-image and image-to-text retrieval by cosine similarity. That similarity is powerful for search but is not the same as grounded visual reasoning: the model may match concepts without reading small text, counting objects, or verifying spatial relationships.

Use CLIP-like embeddings for candidate retrieval; use OCR, VLMs, or task-specific verification when the answer requires precise visual facts.

> One-liner: **CLIP finds likely evidence; it does not prove the evidence**.


Related: [[02 Literature Notes/LLM Engineering/Multimodal AI]] · [[02 Literature Notes/LLM Engineering/Embeddings]]
