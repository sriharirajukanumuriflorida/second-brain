# Attention Is Content-Based Soft Lookup

Attention computes, for each token, a weighted average of all tokens' **Values**, where weights come from `softmax(Q·Kᵀ/√d_k)`. The **Query** is what a token looks for, the **Key** is what a token offers, the **Value** is what it passes on. Q·K scores relevance; softmax turns scores into mixing weights.

The `1/√d_k` scale prevents high-dimensional dot products from saturating the softmax. A causal mask (upper triangle → −∞) makes it autoregressive. Multi-head attention runs the operation in parallel subspaces so different heads specialize (syntax, coreference, topic).

> One-liner: **attention = softmax(QKᵀ/√d_k)·V** — a differentiable, content-addressed lookup that mixes information across a sequence.


Related: [[02 Literature Notes/LLM Engineering/Attention Deep-Dive]] · [[03 Permanent Notes/Attention Is Quadratic in Sequence Length]]
