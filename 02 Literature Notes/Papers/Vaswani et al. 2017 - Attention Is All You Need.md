# Vaswani et al. 2017 — Attention Is All You Need

> Primary source behind [[02 Literature Notes/LLM Engineering/Attention Deep-Dive]] and [[02 Literature Notes/LLM Engineering/Transformer Architecture]], and the architecture introduced in [[02 Literature Notes/Courses/Deep Learning - Lesson 12 Transformer Models for NLP]]. This note covers what's in the original paper specifically — the parts the synthesis notes above simplified, cite, or omit — not a re-derivation of attention mechanics already covered there.

## Source
- Paper: Vaswani, Shazeer, Parmar, Uszkoreit, Jones, Gomez, Kaiser, Polosukhin — "Attention Is All You Need," NeurIPS 2017 (arXiv:1706.03762v7)
- PDF: [[07 Resources Library/Deep Learning/Papers/Vaswani et al. 2017 - Attention Is All You Need.pdf]]
- Date added: 2026-11-19

---

## 1. Mental Model

**The paper's actual claim is narrower than its title suggests: you can drop recurrence and convolution from sequence transduction entirely and get better translation quality, more parallelism, and less training time, using attention alone.** It's an empirical architecture paper (introducing the encoder-decoder Transformer for machine translation), not a general theory of attention — the generative, decoder-only, pretrain-everything paradigm (GPT, BERT) came later, built on this architecture.

> Key intuition: every prior sequence model (RNN, LSTM, ConvS2S) processed tokens through a chain of positions, step by step or layer by layer with limited receptive field. The Transformer instead connects **any two positions with a constant number of operations**, at the cost of quadratic compute in sequence length — a trade the paper makes deliberately and justifies with a direct complexity comparison (Table 1), not just empirical results.

---

## 2. What's in the Paper Specifically (Beyond the Synthesis Notes)

### 2.1 Table 1 — the actual argument for self-attention
The paper justifies replacing recurrence/convolution with a complexity table comparing self-attention, recurrent, convolutional, and restricted self-attention layers on three axes: complexity per layer, minimum sequential operations (parallelizability), and maximum path length between any two positions. Self-attention wins on path length (O(1)) and sequential ops (O(1)) whenever sequence length n < representation dimension d — true for typical sentence-level translation, which is why the paper frames this as the practical regime, not a universal win (for very long sequences, restricted/local attention is proposed as the fallback).

### 2.2 Sinusoidal positional encoding — the specific formula
`PE(pos, 2i) = sin(pos / 10000^(2i/d_model))`, `PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))`. The paper picked this specific form (rather than learned positional embeddings, which it reports performed "nearly identically") because sinusoids let the model extrapolate to sequence lengths longer than any seen during training — for any fixed offset k, `PE(pos+k)` is a linear function of `PE(pos)`, so relative position is linearly recoverable. This is the direct ancestor of RoPE (mentioned in [[02 Literature Notes/LLM Engineering/Transformer Architecture]]) but is additive to the embedding, not a rotation applied inside attention.

### 2.3 Why scale by √d_k
Section 3.2.1 gives the specific mechanical reason for the `/√d_k` in `softmax(QKᵀ/√d_k)V`: for large d_k, the dot products `q·k` grow large in magnitude (assuming components are independent, mean-0, variance-1, the dot product has variance d_k), pushing softmax into regions with extremely small gradients. The scale factor counteracts this growth — it's a numerical-stability fix for the softmax's saturation behavior, not a conceptual part of the attention mechanism itself.

### 2.4 Why multi-head rather than one large head
The paper explicitly tests this trade-off: single-head attention with full dimensionality "averages" independent representation subspaces together, which it argues inhibits the model from jointly attending to information from different representation subspaces at different positions. 8 heads of d_model/8 dimensions each is the specific configuration tested; the total compute cost is kept similar to single-head full-dimension attention by shrinking each head proportionally.

### 2.5 Three distinct uses of attention in the original architecture
The original model is encoder-decoder (not decoder-only, which is what modern LLMs actually use): (1) encoder self-attention — full, unmasked, bidirectional; (2) decoder masked self-attention — causal mask prevents attending to future positions, preserving the auto-regressive property; (3) encoder-decoder cross-attention — decoder queries attend over encoder output keys/values, directly analogous to attention mechanisms in earlier seq2seq-with-attention work (Bahdanau et al.). Modern decoder-only LLMs (GPT-family) keep only (2) and drop the encoder and cross-attention entirely — a simplification worth being explicit about, since the paper's diagram (Figure 1) still shows the full encoder-decoder stack.

### 2.6 Why self-attention over convolutions specifically
A single convolutional layer with kernel width k < n does not connect all pairs of positions — it needs a stack of O(n/k) layers (contiguous kernels) or O(log_k(n)) layers (dilated) to do so. Separable convolutions reduce complexity to roughly match a self-attention layer plus a point-wise feed-forward layer, but the paper notes this is exactly the design it already uses (attention + position-wise FFN) — i.e., the Transformer block can be read as a self-attention layer standing in for a convolution, followed by the same FFN a conv-based architecture would need anyway.

### 2.7 Training specifics (usually omitted downstream)
- Base model: 6 encoder + 6 decoder layers, d_model=512, 8 heads, d_ff=2048, trained for 100k steps (~12 hours on 8 P100 GPUs); big model: d_model=1024, 16 heads, 300k steps (3.5 days).
- Adam with β1=0.9, β2=0.98, ε=1e-9, and a specific warmup-then-decay learning rate schedule: `lrate = d_model^-0.5 · min(step^-0.5, step · warmup_steps^-1.5)` — linear warmup for 4000 steps, then inverse-square-root decay. This schedule (not a fixed or simple step-decay LR) is specific to this paper and widely reused.
- Regularization: residual dropout (rate 0.1) applied to each sublayer's output before the residual add, plus label smoothing (ε_ls = 0.1) — label smoothing hurts perplexity (the model is taught to be less confident) but improves BLEU and accuracy, a trade the paper takes deliberately.

### 2.8 Ablations (Table 3) — what the authors found actually mattered
Varying heads, d_k/d_v, model size, dropout, and positional encoding type in controlled ablations: too few heads (1) hurts quality; too many heads (32) also hurts; reducing d_k hurts quality (attention compatibility is harder to compute with less capacity per head, "not easily determined by a simple dot product"); bigger models are consistently better; dropout is necessary (no dropout overfits); sinusoidal vs. learned positional encoding gave "nearly identical" results — direct empirical support for section 2.2 above.

---

## 3. Design Decisions & Tradeoffs

| Decision | Paper's stated rationale |
|---|---|
| **Self-attention over recurrence/convolution** | O(1) path length and sequential ops when n < d (Table 1); trades per-layer compute (O(n²·d)) for parallelism and shorter gradient paths. |
| **Scale attention scores by √d_k** | Counteracts dot-product variance growth with dimension, which otherwise saturates softmax and kills gradients. |
| **Multi-head over single large head** | Lets different heads attend to different representation subspaces; single head "averages away" this specialization. |
| **Sinusoidal over learned positional encoding** | Nearly identical empirical performance, but sinusoidal extrapolates to unseen sequence lengths via linear relative-position recoverability. |
| **Label smoothing (0.1)** | Improves BLEU/accuracy at the cost of perplexity — the model is deliberately made less overconfident. |
| **Warmup + inverse-sqrt LR decay** | Specific schedule tuned for stable Adam training at this scale; not a generic choice. |

---

## 4. Failure Modes & Gotchas

- Treating Figure 1's full encoder-decoder diagram as "the" Transformer architecture — modern decoder-only LLMs (GPT-family) use only the masked self-attention half, no encoder, no cross-attention.
- Confusing this paper's additive sinusoidal positional encoding with RoPE — they solve the same problem (give the model position information) but mechanically differ (added to embeddings vs. rotation applied inside attention).
- Missing that the √d_k scaling is a numerical-stability patch for softmax saturation, not a fundamental part of "what attention is" — it's easy to over-explain this as more conceptually deep than it is.
- Assuming more heads or larger d_k is always better — the paper's own ablation (Table 3) shows both too few and too many heads hurt quality.
- Citing this paper for "attention" in general when the relevant prior work (Bahdanau et al. 2014) introduced additive attention in RNN seq2seq models first — this paper's contribution is specifically removing recurrence entirely and introducing self-attention + multi-head attention as the complete mechanism.

---

## 5. Self-Check

1. Why does the paper justify self-attention with a complexity table (path length, sequential ops) rather than just reporting BLEU scores?
2. What specific numerical problem does dividing by √d_k solve, and why does it get worse as d_k grows?
3. Why does the original architecture have three distinct places attention is used, and which one(s) do modern decoder-only LLMs drop?
4. What did the paper's own ablation find about increasing the number of attention heads indefinitely?
5. Why does sinusoidal positional encoding generalize to sequence lengths unseen during training, mechanically?

---

## 6. Links
- Domain MOC: [[06 Maps of Content/LLM Engineering Concepts]] · [[06 Maps of Content/Deep Learning Concepts]]
- Downstream synthesis: [[02 Literature Notes/LLM Engineering/Attention Deep-Dive]] · [[02 Literature Notes/LLM Engineering/Transformer Architecture]] · [[02 Literature Notes/Courses/Deep Learning - Lesson 12 Transformer Models for NLP]]
- Related permanent notes: [[03 Permanent Notes/Attention Is Content-Based Soft Lookup]] · [[03 Permanent Notes/Attention Communicates Between Tokens the MLP Computes Within Them]] · [[03 Permanent Notes/Attention Is Quadratic in Sequence Length]] · [[03 Permanent Notes/Transformers Use Attention for Sequence Modeling]]
