# Always Give the Model a Refusal Path

If a prompt demands an answer in a fixed format but gives no legitimate way to say 'I can't', the model will **fabricate** to satisfy the format. The fix is a first-class escape hatch in the contract — e.g. `{"answer": null, "reason": "insufficient context"}` — plus an instruction to use it when context is missing, out of scope, or low-confidence.

This single addition is one of the largest levers on groundedness in RAG: it converts 'confident hallucination' into an honest abstention your system can handle.

> One-liner: **let the model say 'I don't know' in-schema** — otherwise format pressure manufactures hallucinations.


Related: [[02 Literature Notes/LLM Engineering/Prompt Contracts]] · [[02 Literature Notes/LLM Engineering/Groundedness and Faithfulness]]
