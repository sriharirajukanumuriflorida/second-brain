# Attention Communicates Between Tokens the MLP Computes Within Them

A transformer block has two sublayers with distinct roles. **Attention mixes information across positions** (communication) — it's the only place tokens interact. The **MLP transforms each token independently** (computation) — a 4×-wide two-layer network believed to store much of the model's factual/associative knowledge as key-value memories.

Both are wrapped as `x = x + sublayer(norm(x))`, writing to a shared **residual stream** that carries information forward with a clean gradient path. Stack N blocks between an embedding and an unembedding and you have a decoder-only LLM.

> One-liner: **attention = talk between tokens, MLP = think within a token** — the residual stream is the bus they both write to.


Related: [[02 Literature Notes/LLM Engineering/Transformer Architecture]] · [[03 Permanent Notes/Attention Is Content-Based Soft Lookup]]
