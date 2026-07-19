# Multimodal RAG Retrieves Evidence Where It Lives

Text-only RAG fails when the evidence is an image region, chart, scanned page, audio segment, or screenshot. Multimodal RAG indexes and retrieves the appropriate representation: text chunks, OCR, captions, image embeddings, page thumbnails, transcripts, audio embeddings, and timestamps. The answer layer then grounds responses in those retrieved artifacts.

The design choice is pragmatic: convert media to text when sufficient, embed media directly when similarity matters, and call a VLM when visual reasoning is required.

> One-liner: **retrieve in the evidence modality, answer in the reasoning modality**.


Related: [[02 Literature Notes/LLM Engineering/Multimodal AI]] · [[02 Literature Notes/LLM Engineering/Embeddings]]
