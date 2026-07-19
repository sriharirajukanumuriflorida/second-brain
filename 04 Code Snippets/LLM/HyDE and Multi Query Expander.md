# HyDE and Multi Query Expander

> Domain 4 · Query Transformation (HyDE, multi-query, routing). Generate deterministic pseudo-HyDE text and paraphrase probes for broader retrieval.

```python
def hyde(query):
    return f"A technical answer about {query}: definitions, mechanism, tradeoffs, and examples."

def multi_query(query):
    return [query, f"definition and mechanism of {query}", f"failure modes and implementation details for {query}"]

q = "how does MMR improve RAG retrieval"
print("HyDE:", hyde(q))
print("queries:")
for x in multi_query(q): print("-", x)
```


Related: [[04 Code Snippets/LLM/Rule Based Query Router]]
