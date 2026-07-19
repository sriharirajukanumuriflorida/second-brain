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

## 8. Links
- Domain MOC: [[06 Maps of Content/LLM Engineering Concepts]]
- Code: [[04 Code Snippets/LLM/Inspecting a Tokenizer with tiktoken]], [[04 Code Snippets/LLM/Token Counting and Cost Estimation]]
- Distilled: [[03 Permanent Notes/Tokens Are the Unit of Cost and Context]], [[03 Permanent Notes/Subword Tokenization Balances Vocabulary and Sequence Length]]
- Downstream: [[02 Literature Notes/LLM Engineering/Embeddings]], [[02 Literature Notes/LLM Engineering/Chunking Strategies]]
