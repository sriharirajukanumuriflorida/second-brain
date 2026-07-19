# SE Week 03 Graph BFS DFS Traversal

> Week 03 · Data Structures, Algorithms & Complexity. Adjacency-list graph traversal showing BFS shortest-hop order vs DFS reachability order.

```python
from collections import deque

graph = {
    "A": ["B", "C"],
    "B": ["D", "E"],
    "C": ["F"],
    "D": [],
    "E": ["F"],
    "F": [],
}

def bfs(start):
    seen, order, q = {start}, [], deque([start])
    while q:
        node = q.popleft()
        order.append(node)
        for nxt in graph[node]:
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return order

def dfs(start):
    seen, order, stack = set(), [], [start]
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        order.append(node)
        stack.extend(reversed(graph[node]))
    return order

print("BFS:", bfs("A"))
print("DFS:", dfs("A"))
```


Related: [[03 Permanent Notes/SE Week 03 Choosing the Right Data Structure]]
