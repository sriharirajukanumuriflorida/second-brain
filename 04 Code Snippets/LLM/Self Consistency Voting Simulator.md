# Self Consistency Voting Simulator

> Domain 3 · Reasoning Prompt Patterns (CoT, ReAct, self-consistency). Sample several deterministic pseudo-reasoning paths and vote on the final answer.

```python
from collections import Counter

def fake_reasoning_path(question, seed):
    # Simulates noisy reasoning: two paths get it right, one path makes an arithmetic slip.
    numbers = [int(x) for x in question.split() if x.isdigit()]
    answer = sum(numbers)
    if seed % 3 == 0: answer += 1
    return {"trace": f"add {numbers}", "answer": answer}

def self_consistency(question, samples=7):
    paths = [fake_reasoning_path(question, s) for s in range(samples)]
    vote = Counter(p["answer"] for p in paths).most_common(1)[0]
    return vote[0], paths

answer, paths = self_consistency("What is 12 plus 30 plus 5?", samples=7)
print("voted answer:", answer)
print("all answers:", [p["answer"] for p in paths])
```


Related: [[04 Code Snippets/LLM/ReAct Loop With Fake Tools]]
