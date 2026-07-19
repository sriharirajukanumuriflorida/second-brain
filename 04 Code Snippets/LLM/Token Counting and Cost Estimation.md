# Token Counting and Cost Estimation

## Purpose
- Estimate tokens and dollar cost for chat requests before you send them — including the hidden chat-template overhead. This is the core FDE cost-modeling utility.

## Language
- Python

## Snippet
```python
# pip install tiktoken
import tiktoken

# Prices are $ per 1M tokens — update to current values for your model.
PRICING = {
    "gpt-4o-mini": {"in": 0.15, "out": 0.60},
    "gpt-4o":      {"in": 2.50, "out": 10.00},
}

def count_message_tokens(messages, model="gpt-4o-mini"):
    try:
        enc = tiktoken.encoding_for_model(model)
    except KeyError:
        enc = tiktoken.get_encoding("o200k_base")
    # ~3 tokens of wrapping per message + a few priming tokens (approx of the
    # chat template overhead). Exact value varies by model family.
    tokens = 3
    for m in messages:
        tokens += 3 + len(enc.encode(m["content"]))
        if m.get("name"):
            tokens += 1
    return tokens

def estimate_cost(messages, model="gpt-4o-mini", expected_output_tokens=300,
                  calls=1):
    n_in = count_message_tokens(messages, model)
    p = PRICING[model]
    cost_per_call = (n_in * p["in"] + expected_output_tokens * p["out"]) / 1_000_000
    return {
        "input_tokens": n_in,
        "output_tokens": expected_output_tokens,
        "cost_per_call_usd": round(cost_per_call, 6),
        "monthly_usd_at_calls": round(cost_per_call * calls, 2),
    }

if __name__ == "__main__":
    messages = [
        {"role": "system", "content": "You are a concise assistant."},
        {"role": "user", "content": "Summarize the attached contract clause."},
    ]
    print(estimate_cost(messages, model="gpt-4o-mini",
                        expected_output_tokens=400, calls=100_000))
```

## Notes
- **Input tokens are countable exactly; output tokens must be estimated** (you don't know them until generation). Use a realistic average from samples.
- The per-message overhead is an approximation of the chat template — good enough for budgeting, not for exact billing reconciliation.
- Keep `PRICING` current; provider prices change. Treat this as a template, not a source of truth on rates.
- Scale the per-call cost by request volume to answer "what will this cost at N req/month" — the question clients always ask.
- Reduce cost levers exposed here: shorter system prompts, compact formats, capping `max_tokens`, cheaper models for easy calls (model routing).

## Links
- Source note: [[02 Literature Notes/LLM Engineering/Tokenization]]
- Related: [[04 Code Snippets/LLM/Inspecting a Tokenizer with tiktoken]]
