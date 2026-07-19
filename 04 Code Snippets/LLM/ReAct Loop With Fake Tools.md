# ReAct Loop With Fake Tools

> Domain 3 · Reasoning Prompt Patterns (CoT, ReAct, self-consistency). A minimal Thought/Action/Observation loop using local deterministic tools.

```python
def calculator(expr):
    allowed = set("0123456789+-*/() ")
    if not set(expr) <= allowed: raise ValueError("unsafe expression")
    return eval(expr, {"__builtins__": {}}, {})

def fake_react(question):
    transcript = []
    transcript.append(("Thought", "Need exact arithmetic, use calculator."))
    expr = question.replace("What is", "").replace("?", "")
    transcript.append(("Action", f"calculator({expr!r})"))
    obs = calculator(expr)
    transcript.append(("Observation", str(obs)))
    transcript.append(("Final", f"The answer is {obs}."))
    return transcript

for kind, text in fake_react("What is 18 * (7 + 5)?"):
    print(f"{kind}: {text}")
```


Related: [[04 Code Snippets/LLM/Self Consistency Voting Simulator]]
