# LLM Framework Selection Function

> Domain 11 · Framework / Ecosystem Literacy (LangChain vs LlamaIndex vs LangGraph vs DSPy). Choose a framework based on requirements such as RAG depth, stateful agents, integrations, or prompt optimization.

```python
def choose_framework(needs):
    if needs.get("optimize_prompts"):
        return "DSPy", "programmatic prompt/signature optimization"
    if needs.get("stateful_agent") or needs.get("human_in_loop"):
        return "LangGraph", "explicit state machine for durable agent workflows"
    if needs.get("rag_heavy") or needs.get("many_data_sources"):
        return "LlamaIndex", "data connectors, indexing, retrieval abstractions"
    if needs.get("many_integrations") or needs.get("quick_prototype"):
        return "LangChain", "broad integrations and chains"
    if needs.get("production_minimal"):
        return "Raw SDK", "less abstraction, clearer control surface"
    return "Raw SDK", "start simple; add frameworks when pain is concrete"

cases = [{"rag_heavy": True}, {"stateful_agent": True}, {"production_minimal": True}]
for c in cases:
    print(c, "->", choose_framework(c))
```


Related: [[04 Code Snippets/LLM/Framework Lock In Scorer]]
