# Lost In The Middle Probe

> Domain 3 · Context Engineering. Simulate why important evidence buried in the middle of long context is risky.

```python
def position_weight(i, n):
    # Toy U-shaped attention: edges are easier than the middle.
    center = abs((i / max(1, n-1)) - 0.5)
    return 0.5 + center

def score_positions(chunks, keyword):
    n = len(chunks); hits = []
    for i, ch in enumerate(chunks):
        if keyword.lower() in ch.lower():
            hits.append((i, round(position_weight(i, n), 2), ch[:45]))
    return hits

chunks = ["instructions", "irrelevant A", "refund policy: receipt required", "irrelevant B", "user question"]
print(score_positions(chunks, "refund"))
chunks_edge = ["instructions", "refund policy: receipt required", "irrelevant A", "irrelevant B", "user question"]
print(score_positions(chunks_edge, "refund"))
```


Related: [[04 Code Snippets/LLM/Context Budget Assembler]]
