# Bounded ReAct Loop

> Domain 5 · Agent Loops & Planning. A capped observe-act loop

```python
def policy(state): return "finish" if state.get("answer") else "lookup"
def run(max_steps=3):
    state={"trace":[]}
    for _ in range(max_steps):
        a=policy(state)
        if a=="finish": break
        state["answer"]="42"; state["trace"].append(a)
    return state
print(run())
```


Related: [[04 Code Snippets/LLM/Plan Then Execute Agent Skeleton]]
