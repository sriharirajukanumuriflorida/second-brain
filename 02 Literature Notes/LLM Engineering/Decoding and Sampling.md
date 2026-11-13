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

---

## 9. Interview Q&A

**Q: Write the temperature-softmax formula and explain what happens as T→0 and T→∞.**
A: Plain softmax is `p_i = exp(z_i) / Σ exp(z_j)`. Temperature just divides each logit by `T` first: `p_i = exp(z_i/T) / Σ exp(z_j/T)`.

Here's the simple way to see what that does. Softmax cares about the *gaps* between logits, not their raw size. Dividing every logit by `T` also divides the gaps between them by `T`. Shrink the gaps and the distribution gets flatter. Widen the gaps and it gets sharper.

So as `T → 0`, you're dividing by something close to zero, which blows the gaps up toward infinity. The biggest logit ends up miles ahead of the rest, so softmax dumps nearly all its probability on just that one token. That's greedy decoding — always pick the top token.

As `T → ∞`, you're dividing by something huge, so all the gaps shrink toward zero. Every token ends up looking about equally likely, so you're basically sampling at random, ignoring what the model actually prefers.

`T=1` is the middle ground — the model's raw, untouched distribution. Below 1 sharpens it (more confident, more repetitive). Above 1 flattens it (more random, more surprising).

*One-liner: temperature stretches or squashes the gaps between logits — near 0 it collapses to "always pick the top token," near infinity it collapses to "pick randomly," and 1 is the model's natural distribution.*

**Q: Contrast top-k and top-p — why does nucleus (top-p) sampling adapt better?**
A: Both exist for the same reason: if you sample from the raw distribution, every so often you'll draw some bizarre, low-probability token, and one bad token can derail the rest of the sentence. So both top-k and top-p cut off the unlikely tail before sampling — keep only the "plausible" tokens, then sample from those.

Top-k keeps a fixed number of tokens — say, the top 40 — no matter what. The problem: how many tokens are actually plausible changes a lot depending on the sentence. After "The capital of France is", the model is almost certain it's "Paris" — really only one good answer. But top-k=40 still forces 39 near-impossible tokens into the pool, giving them a small but real chance of getting picked. Now take "My favorite color is" — dozens of colors are all reasonable. A small top-k might cut off perfectly good options here.

Top-p fixes this by picking tokens based on *cumulative probability* instead of a fixed count. Sort tokens by probability, and keep adding them until you've covered, say, 90% of the total probability mass. When the model is very sure (one token dominates), that 90% might be reached with just one or two tokens — the pool shrinks automatically. When the model is unsure (probability spread across many tokens), it takes more tokens to reach 90% — the pool grows automatically. Same setting, both situations handled correctly.

*One-liner: top-k always keeps the same number of candidates, which is wrong whenever the model's confidence changes — top-p keeps however many tokens are needed to cover a target probability, so it naturally shrinks when the model is sure and grows when it's unsure.*

**Q: When is beam search appropriate, and when is it actively harmful?**
A: It depends on whether there's one "correct" answer to aim for, or many equally good ones.

Beam search doesn't commit to one word at a time like greedy decoding does. Instead it tracks several candidate sentences at once (say, the top 5) and at the end picks whichever full sentence had the highest overall probability. This lets it recover from an early word choice that looked good in the moment but led somewhere worse.

For translation or summarization, there's usually a "right" target to land on — translating a sentence into French has a correct answer, more or less. Beam search's habit of hunting for the single most likely full sentence is exactly what you want there.

For open chat or creative writing, there's no single right continuation — many different replies are all equally good. But beam search still tries to find the single "most likely" sentence, and that sentence tends to be the blandest, safest, most predictable one — because any interesting or unusual word choice drags the probability down a bit, and beam search punishes that. The result is repetitive, generic-sounding text. This is a well-known failure mode called beam search degeneration.

*One-liner: beam search hunts for the one most probable full sentence — great when there's a real target answer (translation), bad for open-ended chat or creative writing, where it just produces bland, repetitive text.*

**Q: What decoding settings would you use for an agent's JSON tool-call output, and why exactly?**
A: Think about what happens when the output is wrong. A tool call gets parsed by code — a JSON parser, a validator. There's no "close enough." Either it parses correctly or it breaks. Unlike a chat reply, there's no benefit to a slightly different word choice here — a different-but-still-valid JSON payload isn't something you ever want 10% of the time.

That means any randomness is pure risk with zero upside. If temperature is above 0, there's always some small chance the model picks a token that breaks the schema — wrong punctuation, wrong type, a made-up field — purely by chance, not because the model didn't know better. At temperature=0, the model just picks the token it's already most confident in, which is almost always the correct one if it's been prompted properly.

So: temperature=0 (greedy). Top-k and top-p don't even apply here, since they only matter when you're sampling with some randomness — at greedy decoding there's only one candidate token at each step anyway. For extra safety, you can pair this with constrained decoding, which blocks any token that would break the JSON grammar at the source — temperature=0 makes bad output unlikely, constrained decoding makes it impossible.

*One-liner: for tool-call JSON, randomness only hurts and never helps, so use temperature=0 — it reliably picks the correct token, and top-k/top-p have nothing left to do.*

**Q: Is temperature=0 fully deterministic? What can still cause different outputs across runs?**
A: Close, but not guaranteed bit-for-bit — and the reason why says something real about how these models run in production.

In theory, temperature=0 just means "always pick the highest-probability token." Same input, same logits, same pick, every time. No randomness in the decision itself.

But in practice, a few things can quietly change the logits by a tiny amount before you even get to that decision. GPU math isn't perfectly consistent — adding the same numbers in a different order can give a microscopically different result due to rounding. And production servers usually batch multiple users' requests together for efficiency; which requests get batched together changes from call to call, which can shift that rounding slightly too. Some serving optimizations add their own small sources of noise as well.

Normally this tiny noise doesn't matter. But every so often, two tokens are almost exactly tied in probability, and that tiny noise is enough to flip which one is technically higher. Since the model always just picks the top one with no tolerance for "basically equal," that flip changes the output — and once one token changes, everything generated after it can end up different too.

*One-liner: temperature=0 removes randomness from the decision ("always pick the top token"), but not from the math that produces the logits — tiny floating-point and batching differences can occasionally flip a near-tied top token, causing rare differences even at "deterministic" settings.*

## 8. Links
- Domain MOC: [[06 Maps of Content/LLM Engineering Concepts]]
- Code: [[04 Code Snippets/LLM/Temperature Top-k Top-p Sampler]], [[04 Code Snippets/LLM/Temperature Reshapes the Distribution]]
- Distilled: [[03 Permanent Notes/Decoding Is a Policy Over the Models Distribution]], [[03 Permanent Notes/Set Temperature Zero for Structured and Evaluated Output]]
- Upstream: [[02 Literature Notes/LLM Engineering/Transformer Architecture]] · Downstream: [[02 Literature Notes/LLM Engineering/Structured Generation]]
