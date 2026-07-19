# Multi-Agent Blackboard Store

> Domain 5 · Multi-Agent Orchestration. Shared state with provenance

```python
board={"facts":[],"risks":[]}
def post(slot, author, text): board[slot].append({"author":author,"text":text})
post("facts","researcher","schemas matter")
post("risks","critic","coordination cost")
print(board)
```


Related: [[04 Code Snippets/LLM/Supervisor Worker Mini Orchestrator]]
