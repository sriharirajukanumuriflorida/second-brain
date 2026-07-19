# Decoding & Sampling

> Topic package — Domain 2 · Roadmap Weeks 10/11.
> Depth goal: understand how logits become tokens, implement the main sampling strategies, and know which knobs to turn for factual vs creative outputs.

## Source
- Track: LLM Engineering (self-directed, FDE roadmap)
- Slide deck: `07 Resources Library/LLM Engineering/Slides/Lesson_09_Decoding_and_Sampling.pptx`
- Hands-on notebook: `07 Resources Library/LLM Engineering/Notebooks/09_Decoding_and_Sampling.ipynb` (runs offline)
- Reference reading: Holtzman et al. 'The Curious Case of Neural Text Degeneration' (nucleus sampling, arXiv:1904.09751); OpenAI API docs (temperature/top_p); HuggingFace generation docs; Fan et al. top-k
- Builds on: [[02 Literature Notes/LLM Engineering/Transformer Architecture]]
- Date: 2026-07-18

---

## 1. Mental Model

**A language model doesn't output text — it outputs a probability distribution over the next token, and decoding is how you pick from it.** At each step the model produces a vector of logits (one per vocabulary token); a softmax turns them into probabilities; a *decoding strategy* selects the next token; that token is appended and the process repeats (autoregression).

The strategy is a product decision, not a model property: the same weights produce a deterministic factual answer or a wild creative riff depending purely on how you sample. Temperature, top-k, and top-p are the three dials.

> Key intuition: **the model gives you a distribution; decoding is your policy for turning it into a choice.** Low-randomness policies (greedy, low temperature) for correctness; higher-randomness (temperature, nucleus) for diversity.

```mermaid
flowchart LR
    H[hidden state] --> L[logits over vocab]
    L --> T[/ temperature]
    T --> F[top-k / top-p filter]
    F --> S[softmax -> probs]
    S --> P[sample or argmax]
    P --> TOK[next token]
    TOK -->|append + repeat| H
```

---

## 2. How It Actually Works

### 2.1 From logits to probabilities
The final layer emits logits `z ∈ R^vocab`. **Temperature** `T` rescales them before softmax:

$$p_i = \frac{\exp(z_i / T)}{\sum_j \exp(z_j / T)}$$

- `T → 0`: distribution collapses to the argmax (greedy, deterministic).
- `T = 1`: the model's raw distribution.
- `T > 1`: flatter, more random, more surprising (and more error-prone).

### 2.2 Greedy and beam search
**Greedy** always takes the argmax — fast, deterministic, but myopic and prone to bland, repetitive text. **Beam search** keeps the `b` highest-probability *sequences* at each step, exploring a small tree, then returns the most probable full sequence. Beam is great for closed-ended tasks (translation, where there's a 'right' answer) but produces generic, repetitive text for open-ended generation and is rarely used for chat.

### 2.3 Top-k and top-p (nucleus) sampling
Pure sampling from the full distribution occasionally picks absurd low-probability tokens. Two truncation fixes:
- **Top-k**: keep only the k highest-probability tokens, renormalize, sample. Simple but k is fixed regardless of how peaked/flat the distribution is.
- **Top-p (nucleus)**: keep the smallest set of tokens whose cumulative probability ≥ p, renormalize, sample. Adapts the candidate set size to the model's confidence — the standard for open-ended generation.

### 2.4 Repetition and other penalties
LLMs can loop ("the the the"). **Repetition penalty** / **frequency & presence penalties** down-weight tokens already produced. **min-p** and **typical sampling** are newer alternatives. These are guardrails on top of the base strategy, not replacements.

### 2.5 Determinism and reproducibility
`temperature=0` (greedy) is the closest to deterministic, but true reproducibility also needs a fixed seed and can still vary across hardware/batching due to floating-point non-associativity. For evals and structured output you generally want `temperature=0`; for content generation you want controlled randomness.

---

## 3. Implementation

Assumed stack: `numpy`. Snippets implement the full sampler zoo. Snippets:
- [[04 Code Snippets/LLM/Temperature Top-k Top-p Sampler]]
- [[04 Code Snippets/LLM/Temperature Reshapes the Distribution]]

### Temperature Top-k Top-p Sampler
A single sampler function covering temperature, top-k and nucleus (top-p).
```python
import numpy as np
def sample_next(logits, temperature=1.0, top_k=0, top_p=0.0, rng=None):
    rng = rng or np.random.RandomState(0)
    logits = logits.astype(float)
    if temperature <= 0:                       # greedy
        return int(logits.argmax())
    logits = logits / temperature
    probs = np.exp(logits - logits.max()); probs /= probs.sum()
    if top_k and top_k < len(probs):           # top-k truncation
        keep = np.argsort(probs)[-top_k:]
        mask = np.zeros_like(probs, bool); mask[keep] = True
        probs = np.where(mask, probs, 0)
    if top_p:                                  # nucleus truncation
        order = np.argsort(probs)[::-1]
        csum = np.cumsum(probs[order])
        cutoff = order[csum <= top_p]
        cutoff = cutoff if len(cutoff) else order[:1]
        mask = np.zeros_like(probs, bool); mask[cutoff] = True
        probs = np.where(mask, probs, 0)
    probs /= probs.sum()
    return int(rng.choice(len(probs), p=probs))

logits = np.array([2.0, 1.0, 0.5, 0.1, -1.0, -3.0])
print("greedy     :", sample_next(logits, temperature=0))
print("T=1.2 top_p:", sample_next(logits, temperature=1.2, top_p=0.9))
```

### Temperature Reshapes the Distribution
Show numerically how temperature flattens or sharpens the softmax.
```python
import numpy as np
def softmax_T(z, T):
    z = np.array(z, float) / T
    e = np.exp(z - z.max()); return e / e.sum()

logits = [3.0, 2.0, 1.0, 0.0]
for T in (0.25, 0.5, 1.0, 2.0):
    p = softmax_T(logits, T)
    print(f"T={T:>4}  probs={np.round(p,3)}  entropy={-(p*np.log(p)).sum():.2f}")
# low T -> peaked (near one-hot, low entropy); high T -> flat (high entropy)
```

---

## 4. Design Decisions & Tradeoffs

| Decision | Guidance |
|---|---|
| **Factual / structured output** | temperature=0 (greedy). Deterministic, no creative drift, best for JSON/tools/evals. |
| **Balanced chat** | temperature ~0.7 + top_p ~0.9. The common default. |
| **Creative / brainstorming** | temperature 0.9-1.2 + top_p 0.95. More diversity, more risk of errors. |
| **Top-k vs top-p** | Prefer top-p (nucleus) — it adapts to model confidence; top-k is a cruder fixed cutoff. |
| **Beam search** | Only for closed-ended tasks (translation/summarization with a target); avoid for open chat. |
| **Repetition control** | Add frequency/presence penalty if you see loops; don't over-penalize or output degrades. |

---

## 5. Failure Modes & Gotchas

- Using temperature>0 for structured/JSON output → occasional schema-breaking tokens.
- Setting BOTH high temperature and high top_p for factual tasks → hallucination risk up.
- Expecting temperature=0 to be bit-for-bit reproducible across hardware → floating-point non-associativity.
- Beam search for chat → generic, repetitive, 'safe' text.
- Cranking temperature to 'be more creative' when the real fix is a better prompt.
- Confusing temperature and top_p as the same dial — they compose (temp reshapes, top_p truncates).

---

## 6. FDE Angle

- Decoding params are the cheapest reliability lever you have: temperature=0 fixes half of 'the model is inconsistent' complaints instantly.
- For agent/tool pipelines and structured output, temperature=0 is almost always correct — say so in the prompt contract.
- Explaining temperature vs top_p to stakeholders demystifies 'why did the answer change?'.
- Deliverable: a documented decoding profile per use case (factual=0, creative=0.9) in the system config.

---

## 7. Self-Check

1. Write the temperature-softmax formula and explain T→0 and T→∞.
2. Contrast top-k and top-p; why does nucleus adapt better?
3. When is beam search appropriate and when is it harmful?
4. What decoding settings would you use for JSON tool output, and why?
5. Is temperature=0 fully deterministic? What can still vary?

## 8. Links
- Domain MOC: [[06 Maps of Content/LLM Engineering Concepts]]
- Code: [[04 Code Snippets/LLM/Temperature Top-k Top-p Sampler]], [[04 Code Snippets/LLM/Temperature Reshapes the Distribution]]
- Distilled: [[03 Permanent Notes/Decoding Is a Policy Over the Models Distribution]], [[03 Permanent Notes/Set Temperature Zero for Structured and Evaluated Output]]
- Upstream: [[02 Literature Notes/LLM Engineering/Transformer Architecture]] · Downstream: [[02 Literature Notes/LLM Engineering/Structured Generation]]
