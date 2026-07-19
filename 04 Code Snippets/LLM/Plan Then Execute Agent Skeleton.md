# Plan Then Execute Agent Skeleton

> Domain 5 · Agent Loops & Planning. Plan steps then execute with checks

```python
plan=["search","compute","verify"]
state={"done":[]}
for step in plan:
    state["done"].append(step)
    if step=="verify": state["status"]="done"
print(state)
```


Related: [[04 Code Snippets/LLM/Bounded ReAct Loop]]
