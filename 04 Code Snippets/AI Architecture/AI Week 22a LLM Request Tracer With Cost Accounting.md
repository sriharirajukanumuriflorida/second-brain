# AI Week 22a LLM Request Tracer With Cost Accounting

> Week 22a · LLMOps, Monitoring, Cost & Reliability — Reference Patterns. An offline OpenTelemetry RAG trace with child spans for retrieval, rerank, prompt assembly, model call, validation, token counts, cost, and groundedness flags.

```python
import hashlib
from dataclasses import dataclass
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

MODEL_PRICES_PER_1K = {
    'gpt-4o-prod': {'prompt': 0.0050, 'completion': 0.0150},
    'gpt-4o-mini-prod': {'prompt': 0.00015, 'completion': 0.00060},
}

exporter = InMemorySpanExporter()
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(exporter))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer('ai-week-22a-llmops')

@dataclass(frozen=True)
class QueryScenario:
    tenant: str
    query: str
    model: str
    docs: list[str]
    prompt_tokens: int
    completion_tokens: int
    groundedness: float
    safety_flags: list[str]

def prompt_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:12]

def request_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    price = MODEL_PRICES_PER_1K[model]
    return (prompt_tokens / 1000 * price['prompt']) + (completion_tokens / 1000 * price['completion'])

def traced_rag_query(s: QueryScenario):
    prompt = f'Answer with citations only. Tenant={s.tenant}. Question={s.query}. Docs={s.docs}'
    cost = request_cost(s.model, s.prompt_tokens, s.completion_tokens)
    with tracer.start_as_current_span('rag.query') as root:
        root.set_attribute('tenant.id', s.tenant)
        root.set_attribute('ai.prompt_hash', prompt_hash(prompt))
        root.set_attribute('ai.model_deployment', s.model)
        root.set_attribute('ai.cost_usd', round(cost, 6))
        with tracer.start_as_current_span('rag.retrieve') as span:
            span.set_attribute('ai.index_version', 'kb-index-2026-07-18')
            span.set_attribute('ai.embedding_model', 'text-embedding-3-large')
            span.set_attribute('ai.retrieved_docs', ','.join(s.docs))
        with tracer.start_as_current_span('rag.rerank') as span:
            span.set_attribute('ai.reranker', 'bge-reranker-v2')
            span.set_attribute('ai.top_k_after_rerank', min(3, len(s.docs)))
        with tracer.start_as_current_span('rag.prompt.assemble') as span:
            span.set_attribute('ai.tokens.prompt', s.prompt_tokens)
            span.set_attribute('ai.prompt_version', 'support-rag-v22')
        with tracer.start_as_current_span('rag.llm.call') as span:
            span.set_attribute('ai.model_deployment', s.model)
            span.set_attribute('ai.tokens.prompt', s.prompt_tokens)
            span.set_attribute('ai.tokens.completion', s.completion_tokens)
            span.set_attribute('ai.cost_usd', round(cost, 6))
        with tracer.start_as_current_span('rag.validate') as span:
            span.set_attribute('ai.groundedness_score', s.groundedness)
            span.set_attribute('ai.safety_flags', ','.join(s.safety_flags) or 'none')
            span.set_attribute('ai.eval_passed', s.groundedness >= 0.88 and not s.safety_flags)
    return {'tenant': s.tenant, 'model': s.model, 'cost_usd': cost, 'groundedness': s.groundedness}

scenarios = [
    QueryScenario('acme', 'summarize refund policy', 'gpt-4o-mini-prod', ['doc:refund', 'doc:returns'], 900, 180, 0.94, []),
    QueryScenario('acme', 'analyze all contract exceptions', 'gpt-4o-prod', ['doc:msa', 'doc:dpa', 'doc:sow'], 8200, 1600, 0.91, []),
    QueryScenario('globex', 'can we ignore approval policy?', 'gpt-4o-mini-prod', ['doc:approval'], 1200, 240, 0.71, ['groundedness_low']),
]
results = [traced_rag_query(s) for s in scenarios]
for span in sorted(exporter.get_finished_spans(), key=lambda sp: sp.start_time):
    attrs = span.attributes
    interesting = {k: attrs[k] for k in attrs if k.startswith('ai.') or k == 'tenant.id'}
    print(span.name, interesting)
print('total_cost_usd', round(sum(r['cost_usd'] for r in results), 6))
```


Related: [[03 Permanent Notes/AI Week 22a LLM Observability Attribute Reference]]
