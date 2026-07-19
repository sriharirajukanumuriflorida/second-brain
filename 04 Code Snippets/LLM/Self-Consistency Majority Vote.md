# Self-Consistency Majority Vote

> Domain 2 · Reasoning Models & Test-Time Compute. Sample N reasoning chains and majority-vote the final answer.

```python
from collections import Counter

def self_consistency(reason_once, prompt, n=5):
    # reason_once(prompt) -> (chain_text, final_answer)
    answers = []
    for _ in range(n):
        _, ans = reason_once(prompt)
        answers.append(ans)
    vote = Counter(answers).most_common(1)[0]
    return vote[0], vote[1] / n            # answer, agreement fraction

# demo: a noisy 'reasoner' right 60% of the time
import random; random.seed(0)
def noisy_reasoner(prompt):
    ans = 42 if random.random() < 0.6 else random.choice([41, 43, 44])
    return "...steps...", ans

ans, agree = self_consistency(noisy_reasoner, "what is 6*7?", n=15)
print(f"majority answer={ans}  agreement={agree:.0%}")   # majority recovers 42
```


Related: [[04 Code Snippets/LLM/Match Test-Time Compute to Difficulty]]
