# Tokenization

> Topic package — Domain 1 (Data Representation) · Roadmap Week 09.
> Depth goal: understand how text becomes token IDs, why it drives cost/context/quirks, and be able to inspect and reason about any tokenizer.

## Source
- Track: LLM Engineering (self-directed, FDE roadmap)
- Slide deck: `07 Resources Library/LLM Engineering/Slides/Lesson_02_Tokenization.pptx`
- Hands-on notebook: `07 Resources Library/LLM Engineering/Notebooks/02_Tokenization.ipynb` (runs offline)
- Reference reading: OpenAI tiktoken docs; Sennrich et al. "Neural MT with Subword Units" (BPE, arXiv:1508.07909); Kudo "Subword Regularization" (Unigram/SentencePiece); Karpathy "Let's build the GPT Tokenizer"; HuggingFace Tokenizers docs
- Date: 2026-07-18

---

## 1. Mental Model

**Models don't see text — they see integers.** A tokenizer is the deterministic function that maps a string to a sequence of integer **token IDs** (and back). Each ID indexes a row in the model's embedding matrix. Everything the model knows about "words" is mediated by this vocabulary.

Why not just split on words or characters?
- **Words**: the vocabulary would be enormous and still miss rare/new/misspelled words ("out-of-vocabulary" problem). Every typo becomes an unknown.
- **Characters**: sequences become extremely long (one ID per letter), wasting the model's limited context and compute.

**Subword tokenization** is the compromise everyone uses: frequent words become a single token, rare words break into meaningful pieces ("tokenization" → `token` + `ization`), and *any* string is representable by falling back to bytes. This gives a fixed, modest vocabulary (~30k–200k) that covers all possible input.

> Key intuition: **the token is the atomic unit of cost, context, and pricing.** Context windows are measured in tokens, APIs bill per token, and latency scales with token count. If you can't reason about tokens, you can't reason about LLM cost or limits.

---

## 2. How It Actually Works

### 2.1 Byte-Pair Encoding (BPE) — the dominant algorithm
BPE (used by GPT-2/3/4, Llama, and most modern LLMs) is learned from a corpus:

1. Start with a base vocabulary of individual bytes/characters.
2. Count all adjacent symbol pairs in the corpus.
3. **Merge** the most frequent pair into a new single token; record the merge rule.
4. Repeat until you reach the target vocabulary size.

The learned artifact is an **ordered list of merge rules**. At encode time, the tokenizer greedily applies those merges to incoming text. Because it can always fall back to raw bytes, **byte-level BPE has zero out-of-vocabulary** — any Unicode string, emoji, or binary blob is representable.

### 2.2 Other families (know they exist)
- **WordPiece** (BERT) — like BPE but merges by likelihood gain rather than raw frequency; marks continuation with `##`.
- **Unigram / SentencePiece** (T5, many multilingual/Llama-adjacent) — starts big and *prunes* tokens probabilistically; treats text as raw bytes with no pre-tokenization, so it handles languages without spaces.

### 2.3 Special tokens
Beyond text, the vocabulary reserves **special tokens** with structural meaning: `<|endoftext|>`, beginning/end-of-sequence, padding, and — crucially for LLMs — **chat template tokens** (`<|im_start|>`, role markers). The chat template that wraps your messages is itself tokenized; mis-formatting it silently degrades model behavior.

### 2.4 The economics (why this matters daily)
- **~4 characters ≈ 1 token** for typical English; ~0.75 words per token. This ratio is a rule of thumb, not a law — it shifts by language and content.
- **Non-English and code cost more tokens** per idea: languages with non-Latin scripts, or whitespace-heavy code, fragment into more tokens → higher cost and faster context exhaustion.
- **Numbers and rare strings** tokenize inefficiently (often digit-by-digit), which is part of why LLMs struggle with arithmetic and long IDs.

### 2.5 The math you should hold
Context/cost is linear in token count `n`:

$$\text{cost} = n_{\text{in}} \cdot p_{\text{in}} + n_{\text{out}} \cdot p_{\text{out}}, \qquad n \le C \text{ (context window)}$$

Compression ratio of a tokenizer on a text = `characters / tokens`; higher is cheaper. This is exactly what you compare when choosing between models/tokenizers for a non-English or code-heavy workload.

---

## 3. Implementation

Assumed stack (pin these): `tiktoken>=0.7` (OpenAI), `transformers>=4.44` / `tokenizers` (open models). See snippets:
- [[04 Code Snippets/LLM/Inspecting a Tokenizer with tiktoken]]
- [[04 Code Snippets/LLM/Token Counting and Cost Estimation]]

### 3.1 Encode / decode round-trip
```python
import tiktoken
enc = tiktoken.get_encoding("o200k_base")   # gpt-4o family; cl100k_base for gpt-4/3.5
ids = enc.encode("Tokenization drives cost.")
print(ids)                       # e.g. [2500, 2065, ...] integer token IDs
print([enc.decode([i]) for i in ids])   # the string piece each ID maps to
print(enc.decode(ids))           # exact round-trip back to the original string
```

### 3.2 Count tokens for a chat request (the real cost)
```python
def count_message_tokens(messages, model="gpt-4o-mini"):
    enc = tiktoken.encoding_for_model(model)
    # Approximate the chat wrapping overhead (~3 tokens/message + priming).
    n = sum(3 + len(enc.encode(m["content"])) for m in messages) + 3
    return n
```

### 3.3 Inspecting an open-model tokenizer
```python
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B")
print(tok.tokenize("internationalization"))   # subword pieces
print(tok.vocab_size, tok.special_tokens_map)
```

---

## 4. Design Decisions & Tradeoffs

| Decision | Guidance |
|---|---|
| **Which tokenizer to reason with** | Always match the *model you're actually calling*. `o200k_base` for gpt-4o/4.1; `cl100k_base` for gpt-4/3.5/text-embedding-3; each open model ships its own. |
| **Budgeting context** | Count tokens, never characters/words. Leave headroom for the model's output (`max_tokens`) inside the context window. |
| **Non-English / code workloads** | Compare tokenizers' compression ratios on *your* data — a model that's cheaper per-token may be more expensive per-request if it fragments your language. |
| **Chunk sizing (links to Chunking)** | Chunk size is a token budget; measure with the embedding model's tokenizer. |
| **Prompt engineering** | Fewer tokens = cheaper + faster + more room. Terse system prompts and compact formats (no gratuitous JSON whitespace) save real money at scale. |

---

## 5. Failure Modes & Gotchas

- **Counting characters instead of tokens** → surprise context-overflow errors and mis-estimated bills.
- **Using the wrong tokenizer** for the model → off-by-10–20% token counts; budgets and truncation go wrong.
- **Forgetting chat-template overhead** → each message adds hidden tokens; long conversations overflow sooner than a naive sum suggests.
- **Assuming a token = a word** → breaks badly for code, non-English, numbers, and URLs.
- **Trusting the model with exact-character tasks** (reverse a string, count letters) → tokenization hides characters inside merged tokens; the model literally can't see them.
- **Ignoring trailing spaces / leading-space tokens** → `" token"` and `"token"` are *different* IDs; this trips up few-shot formatting and stop sequences.

---

## 6. FDE Angle

- **Cost modeling is a tokenization exercise.** When a client asks "what will this cost at 1M requests/month," you estimate input+output tokens per request and multiply. Being fluent here builds credibility fast.
- **Non-English clients**: flag early that token costs differ by language; it changes model selection and budget.
- **Context-limit incidents** are usually token-accounting bugs (chat overhead, retrieved-context bloat). Knowing where the tokens go is the debugging skill.
- Deliverable: a **token/cost calculator** for the client's actual prompt shapes — cheap to build, high perceived value.

---

## 7. Self-Check

1. Why does byte-level BPE never have out-of-vocabulary tokens?
2. Explain to a PM why a Japanese prompt costs more than the "same" English prompt.
3. From memory, count the tokens in a 3-message chat request including overhead.
4. Which tokenizer do gpt-4o and text-embedding-3 use, and why must you match it?
5. Why do LLMs struggle to reverse a string or do long addition — tie it to tokenization.
6. Given $0.15/1M input + $0.60/1M output tokens, estimate cost for 800-in/400-out over 100k calls.

---

## 9. Interview Q&A

**Q: Why does byte-level BPE never have out-of-vocabulary tokens?**
A: Think about what "out-of-vocabulary" actually means: a piece of text the tokenizer has no way to represent at all. Word-level tokenizers run into this constantly — if a word wasn't in the training vocabulary (a typo, a brand-new slang term, a name), there's simply no ID for it, and the tokenizer has to give up and output some generic "unknown" placeholder, which loses real information.

Byte-level BPE avoids this by building its vocabulary from the ground up, starting with individual bytes rather than whole words. Every possible byte value (0-255) is already a valid token before any merging even happens. The BPE learning process then merges *common* pairs of bytes/characters into bigger, more efficient tokens — but the individual bytes are always still there as a fallback. So if the tokenizer runs into a word, emoji, or string of symbols it has never seen before, worst case it just falls back to spelling it out byte by byte, using tokens it already has. It never needs a brand-new, undefined symbol, because every possible input was already representable from the very first step.

This is exactly why this approach works for emojis, typos, rare technical terms, even raw binary data — anything that can be expressed as bytes (which is everything digital) has a path through the vocabulary, even if that path is inefficient (using many small tokens instead of one big one).

*One-liner: byte-level BPE starts from individual bytes, which already cover every possible input, and only merges common patterns into bigger tokens on top of that — so anything unfamiliar can always fall back to being spelled out byte by byte instead of hitting a missing, undefined token.*

**Q: Explain to a non-technical person why a Japanese prompt costs more than the "same" English prompt.**
A: Here's the simple version: the AI doesn't read in words — it reads in small chunks called tokens, and you're charged based on how many of those chunks your text breaks into, not how many words or characters it has.

Most AI tokenizers were trained mostly on English text, so they're very efficient at breaking English into few, large chunks — common English words often become just one token each. But the same tokenizer sees Japanese far less often during its training, and Japanese also uses a completely different writing system. So when it tries to break Japanese text into tokens, it often can't find big, efficient whole-word chunks to use — it ends up breaking the text into many more, smaller pieces to represent the same sentence.

So even though a Japanese sentence and its English translation mean exactly the same thing, the Japanese one can end up needing noticeably more tokens to represent — sometimes twice as many or more. Since cost is based on tokens, not meaning, that same idea literally costs more money to send to the AI in Japanese than in English, purely because of how the tokenizer happens to chop up each language.

*One-liner: cost is based on how many token-chunks your text breaks into, and tokenizers (mostly trained on English) are less efficient at breaking up other languages like Japanese — so the same sentence, meaning the exact same thing, can cost more in Japanese purely because it splits into more pieces.*

**Q: From memory, roughly estimate the tokens in a 3-message chat request, including overhead.**
A: Don't just add up the words in the messages — that undercounts, because chat APIs wrap every message with hidden formatting (something like "this is from the user," "this is from the assistant") and that wrapping costs tokens too, even though you never see it directly.

Work through it step by step. Say you have 3 messages, each roughly 20 words long. Using the rough rule that 1 token is about 0.75 words, 20 words is about 27 tokens of actual content per message. Now add the hidden overhead — a reasonable estimate is about 3-4 extra tokens per message for the role markers and formatting the API adds behind the scenes. So each message is roughly 27 + 3 ≈ 30 tokens, and 3 messages comes to about 90 tokens. Then add a small fixed amount (a few tokens) for the overall request priming, and you land around 95-100 tokens total for something that looks like "just 60 words of text" if you'd only counted the words.

The real lesson isn't the exact number — it's that naively summing up message lengths will always underestimate the real token count, because the hidden per-message wrapping is real cost you're not seeing in the raw text.

*One-liner: estimate words per message, convert to tokens (~0.75 words per token), then add a few extra tokens per message for hidden role/formatting overhead plus a small fixed priming cost — naively summing just the visible words will always undercount the real total.*

**Q: Which tokenizer do GPT-4o and text-embedding-3 use, and why must you match it?**
A: GPT-4o (and the broader GPT-4o/4.1 family) uses a tokenizer called `o200k_base`. Older models like GPT-4 and GPT-3.5, along with the earlier `text-embedding-3`-adjacent models, use a different one called `cl100k_base`. These aren't interchangeable — each model was trained using one specific tokenizer, and that tokenizer's exact vocabulary and merge rules are baked into how the model understands text.

Here's why matching matters: if you count tokens using the wrong tokenizer (say, estimating `cl100k_base` token counts for a prompt you're actually sending to a `o200k_base` model), your count will be off — sometimes by 10-20% or more — because the two tokenizers don't break the same text into the same pieces. That mismatch causes two real problems: your cost estimates will be wrong (you'll budget for the wrong number of billed tokens), and worse, if you're trying to fit text within a model's exact context window, you might think you have more room than you actually do, truncate something incorrectly, or hit an unexpected overflow error — because the number you calculated was never the number the model is actually using.

*One-liner: GPT-4o uses `o200k_base`, older GPT-4/3.5 models use `cl100k_base` — these tokenizers split text differently, so counting tokens with the wrong one gives you a wrong count (often by 10-20%), which throws off both cost estimates and context-window budgeting for the model you're actually calling.*

**Q: Why do LLMs struggle to reverse a string or do long addition — tie it to tokenization.**
A: The core issue is that tokenization often hides individual characters *inside* bigger, merged tokens — so the model frequently never actually "sees" the individual letters or digits it would need to manipulate directly.

Take the word "tokenization." A tokenizer might turn this into just two tokens: `token` and `ization`. The model gets handed those two chunks as a whole, the same way you'd get handed a whole word instead of a pile of individual letters. So when you ask it to "reverse this string," it's being asked to do something character-by-character — but its actual input representation isn't really characters, it's these bigger merged pieces. The model has to somehow reconstruct the individual letters from training experience with how these chunks are usually spelled, rather than directly reading and manipulating them the way code would with a string.

The same problem shows up with numbers and long addition. Multi-digit numbers often get split inconsistently — sometimes as one full number-token, sometimes broken into irregular digit groups, depending on how common that specific number was in training data. This means the model isn't doing addition the way a calculator does (digit by digit, carrying over cleanly) — it's trying to pattern-match on these inconsistent token chunks, which is part of why long addition problems get noticeably less reliable as the numbers get bigger and the digit groupings get messier.

*One-liner: tokenization often merges multiple characters or digits into single tokens, so the model doesn't actually have direct, reliable access to individual letters or digits the way code does — which is exactly why tasks like reversing a string or doing long addition (which require precise character/digit-level manipulation) are unreliable for LLMs.*

**Q: Given $0.15 per 1M input tokens and $0.60 per 1M output tokens, estimate the cost for 800 tokens in / 400 tokens out, over 100,000 calls.**
A: Work this out one call at a time, then scale up — that keeps the arithmetic simple and avoids mixing up input and output pricing partway through.

For one call: 800 input tokens at $0.15 per million tokens costs `800 / 1,000,000 × $0.15 = $0.00012`. Output is 400 tokens at $0.60 per million: `400 / 1,000,000 × $0.60 = $0.00024`. Add those together: one call costs about $0.00036 total.

Now scale to 100,000 calls: `$0.00036 × 100,000 = $36`. So the whole batch of 100,000 calls costs around $36 — split roughly as $12 from input tokens and $24 from output tokens (output costs more per call here, both because output pricing is higher per token and because there are fewer output tokens than input tokens in this example, so it's worth checking which side actually dominates rather than assuming).

The actual habit worth having here isn't memorizing this one calculation — it's being able to do input cost plus output cost, separately, then multiply by call volume, any time someone asks "what will this cost at scale."

*One-liner: compute cost per call by multiplying each token count by its own price per million, add input and output cost together, then multiply by total call volume — here, that's about $0.00036 per call, or roughly $36 total across 100,000 calls.*

## 8. Links
- Domain MOC: [[06 Maps of Content/LLM Engineering Concepts]]
- Code: [[04 Code Snippets/LLM/Inspecting a Tokenizer with tiktoken]], [[04 Code Snippets/LLM/Token Counting and Cost Estimation]]
- Distilled: [[03 Permanent Notes/Tokens Are the Unit of Cost and Context]], [[03 Permanent Notes/Subword Tokenization Balances Vocabulary and Sequence Length]]
- Downstream: [[02 Literature Notes/LLM Engineering/Embeddings]], [[02 Literature Notes/LLM Engineering/Chunking Strategies]]
