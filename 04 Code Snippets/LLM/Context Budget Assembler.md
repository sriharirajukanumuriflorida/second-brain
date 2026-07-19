# Context Budget Assembler

> Domain 3 · Context Engineering. Rank context candidates by relevance density and fit them into a fixed token budget.

```python
def token_count(text):
    return len(text.split())

def assemble_context(instructions, task, candidates, budget):
    fixed = token_count(instructions) + token_count(task)
    remaining = budget - fixed
    scored = sorted(candidates, key=lambda c: c["score"] / max(1, token_count(c["text"])), reverse=True)
    chosen = []
    for c in scored:
        n = token_count(c["text"])
        if n <= remaining:
            chosen.append(c); remaining -= n
    body = "\n\n".join(f"[{c['id']}] {c['text']}" for c in chosen)
    return f"{instructions}\n\nEVIDENCE:\n{body}\n\nTASK:\n{task}", chosen

cands = [{"id":"A","score":0.95,"text":"Refunds require receipt ID and payment date."},
         {"id":"B","score":0.40,"text":"Company picnic is Friday with snacks."}]
ctx, chosen = assemble_context("Answer only from evidence.", "How do refunds work?", cands, budget=30)
print([c["id"] for c in chosen])
print(ctx)
```


Related: [[04 Code Snippets/LLM/Lost In The Middle Probe]]
