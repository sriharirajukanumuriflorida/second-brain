# Match Test-Time Compute to Difficulty

> Domain 2 · Reasoning Models & Test-Time Compute. Route easy queries to one-shot, hard queries to expensive reasoning — a cost gate.

```python
def solve(query, difficulty_fn, cheap_solve, reason_solve, threshold=0.5):
    d = difficulty_fn(query)               # 0..1 estimated difficulty
    if d < threshold:
        return cheap_solve(query), "cheap-1shot", 1
    return reason_solve(query), "reasoning", 10   # ~10x tokens

def difficulty(q):    # toy: longer / has 'prove'/'why' -> harder
    hard = any(w in q.lower() for w in ("prove", "why", "derive", "plan"))
    return 0.9 if hard else 0.2

cheap = lambda q: "quick answer"
reason = lambda q: "answer after long chain-of-thought"
for q in ["What is the capital of France?", "Prove sqrt(2) is irrational"]:
    ans, mode, cost = solve(q, difficulty, cheap, reason)
    print(f"[{mode:>10} cost~{cost:>2}x] {q}")
```


Related: [[04 Code Snippets/LLM/Self-Consistency Majority Vote]]
