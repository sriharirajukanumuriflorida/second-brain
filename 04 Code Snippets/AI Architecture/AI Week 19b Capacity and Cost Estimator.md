# AI Week 19b Capacity and Cost Estimator

> Week 19b · AI Solution Architecture — Applied. Deterministic calculator for tokens, monthly model cost, embedding storage, one-time embedding cost, per-query cost, and p99 latency breakdown.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Workload:
    users: int
    queries_per_user_day: int
    avg_prompt_tokens: int
    avg_response_tokens: int
    prompt_price_per_1k: float
    completion_price_per_1k: float
    embedding_price_per_1k: float
    chunks_per_doc: int
    docs: int
    dims: int
    avg_chunk_tokens: int = 800
    business_days_per_month: int = 22


def estimate(w: Workload) -> dict:
    queries_day = w.users * w.queries_per_user_day
    queries_month = queries_day * w.business_days_per_month
    prompt_month = queries_month * w.avg_prompt_tokens
    completion_month = queries_month * w.avg_response_tokens
    prompt_cost = prompt_month / 1000 * w.prompt_price_per_1k
    completion_cost = completion_month / 1000 * w.completion_price_per_1k
    chunks = w.docs * w.chunks_per_doc
    vector_gb = chunks * w.dims * 4 / 1_000_000_000
    embedding_tokens = chunks * w.avg_chunk_tokens
    embedding_cost = embedding_tokens / 1000 * w.embedding_price_per_1k
    per_query_cost = (w.avg_prompt_tokens / 1000 * w.prompt_price_per_1k) + (w.avg_response_tokens / 1000 * w.completion_price_per_1k)
    latency_ms = {
        "auth": 100,
        "retrieval_rerank": 700,
        "prompt_assembly": 100,
        "model_first_token": 2000,
        "stream_completion": 4500,
        "guardrails_audit": 400,
        "network_app": 200,
    }
    return {
        "queries_day": queries_day,
        "queries_month": queries_month,
        "prompt_tokens_month": prompt_month,
        "completion_tokens_month": completion_month,
        "monthly_llm_cost": prompt_cost + completion_cost,
        "per_query_cost": per_query_cost,
        "embedding_vectors": chunks,
        "embedding_storage_gb_raw": vector_gb,
        "one_time_embedding_cost": embedding_cost,
        "p99_latency_ms": latency_ms,
        "p99_total_ms": sum(latency_ms.values()),
    }


def print_report(label: str, w: Workload) -> None:
    r = estimate(w)
    print(f"\n{label}")
    print(f"queries/day={r['queries_day']:,} queries/month={r['queries_month']:,}")
    print(f"tokens/month prompt={r['prompt_tokens_month']:,} completion={r['completion_tokens_month']:,}")
    print(f"monthly LLM cost=${r['monthly_llm_cost']:,.2f} per query=${r['per_query_cost']:.4f}")
    print(f"embeddings={r['embedding_vectors']:,} raw vector storage={r['embedding_storage_gb_raw']:.2f} GB one-time embedding=${r['one_time_embedding_cost']:,.2f}")
    print(f"p99 total={r['p99_total_ms']} ms breakdown={r['p99_latency_ms']}")

# Illustrative GPT-4o prices: $0.0025 per 1K input tokens and $0.0100 per 1K output tokens.
# Illustrative text-embedding-3-small price: $0.00002 per 1K tokens.
base = Workload(users=50, queries_per_user_day=40, avg_prompt_tokens=1500, avg_response_tokens=800, prompt_price_per_1k=0.0025, completion_price_per_1k=0.0100, embedding_price_per_1k=0.00002, chunks_per_doc=10, docs=40_000, dims=1536)
scaled = Workload(**{**base.__dict__, "users": 500})
print_report("Insurance baseline", base)
print_report("Scale-up to 500 users", scaled)
```


Related: [[03 Permanent Notes/AI Week 19b FDE Discovery to Architecture Playbook]]
