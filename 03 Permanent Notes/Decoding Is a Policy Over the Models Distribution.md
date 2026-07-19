# Decoding Is a Policy Over the Models Distribution

An LLM outputs a probability distribution over the next token; **decoding is your policy for choosing from it**, and it's a product decision independent of the weights. Temperature rescales logits before softmax (low = peaked/deterministic, high = flat/random). Top-k keeps the k most likely tokens; top-p (nucleus) keeps the smallest set covering probability mass p, adapting to the model's confidence.

The same model is a precise fact-answerer at `temperature=0` or a creative writer at `temperature=1.1, top_p=0.95`. Greedy/beam for closed-ended tasks; nucleus sampling for open-ended generation.

> One-liner: **the model proposes a distribution; decoding disposes** — temperature reshapes it, top-k/top-p truncate it, you sample.


Related: [[02 Literature Notes/LLM Engineering/Decoding and Sampling]] · [[03 Permanent Notes/Set Temperature Zero for Structured and Evaluated Output]]
