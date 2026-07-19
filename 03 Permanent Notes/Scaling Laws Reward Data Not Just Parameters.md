# Scaling Laws Reward Data Not Just Parameters

Transformer loss falls as a predictable power law in parameters, data, and compute (Kaplan 2020; Chinchilla 2022). The key correction from Chinchilla: for a fixed compute budget, most large models are **under-trained** — you should train a smaller model on far more tokens (~20 tokens/param) rather than a huge model on few.

Practical consequence: a well-trained 7B on 2T tokens beats a 13B on 300B. Bigger isn't automatically better; the data budget matters as much as the parameter count.

> One-liner: **compute buys loss reduction only if split right between size and data** — under-trained giants lose to well-fed smaller models.


Related: [[02 Literature Notes/LLM Engineering/Transformer Architecture]]
