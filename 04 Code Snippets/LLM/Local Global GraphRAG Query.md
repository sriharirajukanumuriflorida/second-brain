# Local Global GraphRAG Query

> Domain 4 · GraphRAG / Knowledge-Graph RAG. Choose entity-neighborhood retrieval for local questions and community summaries for global questions.

```python
community = {"rag_methods":"RAG methods combine retrieval indexes with LLM synthesis; GraphRAG adds relations and communities."}
graph = {"GraphRAG":[("extends","RAG","doc2"),("uses","knowledge graphs","doc2")],
         "knowledge graphs":[("represent","relations","doc3")]}

def local(entity):
    return [f"{entity} {rel} {dst} [{src}]" for rel, dst, src in graph.get(entity, [])]

def query(q):
    if "overall" in q or "themes" in q: return community["rag_methods"]
    return "\n".join(local("GraphRAG"))

print(query("How does GraphRAG relate to RAG?"))
```


Related: [[04 Code Snippets/LLM/Tiny GraphRAG Index Builder]]
