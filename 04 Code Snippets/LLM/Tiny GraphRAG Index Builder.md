# Tiny GraphRAG Index Builder

> Domain 4 · GraphRAG / Knowledge-Graph RAG. Extract simple entity-relation triples with provenance into an adjacency graph.

```python
from collections import defaultdict

triples = [("RAG", "uses", "retrieval", "doc1"),
           ("GraphRAG", "extends", "RAG", "doc2"),
           ("GraphRAG", "uses", "knowledge graphs", "doc2"),
           ("knowledge graphs", "represent", "relations", "doc3")]

graph = defaultdict(list)
for src, rel, dst, prov in triples:
    graph[src].append({"rel": rel, "dst": dst, "source": prov})

for node, edges in graph.items():
    print(node, "->", edges)
```


Related: [[04 Code Snippets/LLM/Local Global GraphRAG Query]]
