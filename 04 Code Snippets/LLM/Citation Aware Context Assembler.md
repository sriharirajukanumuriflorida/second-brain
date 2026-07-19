# Citation Aware Context Assembler

> Domain 4 · RAG Pipeline Fundamentals. Pack retrieved chunks into a bounded context with stable source labels for grounded generation.

```python
def assemble(hits, max_chars=220):
    blocks, used = [], 0
    for score, chunk_id, text in hits:
        block = f"[{chunk_id} score={score:.2f}] {text}"
        if used + len(block) > max_chars:
            continue
        blocks.append(block); used += len(block)
    instructions = "Answer only from context. Cite chunk ids like [d1]. Refuse if missing."
    return instructions + "\n\n<context>\n" + "\n".join(blocks) + "\n</context>"

hits = [(0.91, "policy-7", "Refunds require a receipt within 30 days."),
        (0.63, "policy-2", "Store credit may be issued after 30 days.")]
print(assemble(hits))
```


Related: [[04 Code Snippets/LLM/Offline Mini RAG Pipeline]]
