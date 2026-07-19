# AI Week 20b Azure Deployment Topology Cost Estimator

> Week 20b · Cloud Architecture & Deployment — Applied. Pydantic v2 model tree for the insurance-underwriter Azure deployment plus a representative monthly line-item cost estimator for Baseline, Growth, and Enterprise scale.

```python
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

# Representative unit prices from Azure pricing pages; verify in-region at deploy time.
PRICES = {
    'gpt4o_input_per_mtok': 2.50,
    'gpt4o_output_per_mtok': 10.00,
    'embedding_3_large_per_mtok': 0.13,
    'containerapp_replica_month': 75.0,
    'postgres_gp_2vc_month': 320.0,
    'postgres_gp_4vc_month': 620.0,
    'postgres_gp_8vc_month': 1240.0,
    'blob_hot_gb_month': 0.018,
    'frontdoor_month': 165.0,
    'log_analytics_ingest_gb': 2.76,
    'private_endpoint_month': 7.30,
    'ptu_month': 6000.0,
}

class Service(BaseModel):
    name: str
    sku: str
    replicas: int = 1
    private_endpoint: bool = True

class Workload(BaseModel):
    label: str
    users: int
    questions_per_user_day: int = 40
    business_days_per_month: int = 22
    prompt_tokens: int = 1500
    response_tokens: int = 800
    cache_hit_rate: float = Field(default=0.0, ge=0.0, le=0.95)
    use_ptu: bool = False
    log_gb_per_day: float = 1.0

class DeploymentTopology(BaseModel):
    name: str
    region: str
    services: list[Service]
    docs: int = 40_000
    chunks_per_doc: int = 10
    embedding_dims: int = 1536
    avg_chunk_tokens: int = 800
    blob_gb: float = 100.0
    private_networking: bool = True
    public_egress_allowed: bool = False
    prompt_registry_blob_url: str
    vector_index_name: str
    chat_model_deployment: str
    embedding_model_deployment: str

    def estimate_monthly_cost(self, workload: Workload) -> dict:
        queries_month = workload.users * workload.questions_per_user_day * workload.business_days_per_month
        billable_queries = queries_month * (1.0 - workload.cache_hit_rate)
        input_mtok = billable_queries * workload.prompt_tokens / 1_000_000
        output_mtok = billable_queries * workload.response_tokens / 1_000_000
        chunks = self.docs * self.chunks_per_doc
        embed_mtok = chunks * self.avg_chunk_tokens / 1_000_000
        vector_gb_raw = chunks * self.embedding_dims * 4 / 1_000_000_000

        postgres_key = 'postgres_gp_2vc_month'
        if workload.users >= 500:
            postgres_key = 'postgres_gp_8vc_month'
        elif workload.users >= 200:
            postgres_key = 'postgres_gp_4vc_month'

        avg_replicas = 2 if workload.users < 200 else 5 if workload.users < 500 else 10
        private_endpoints = sum(1 for s in self.services if s.private_endpoint)
        model_cost = PRICES['ptu_month'] if workload.use_ptu else (
            input_mtok * PRICES['gpt4o_input_per_mtok'] + output_mtok * PRICES['gpt4o_output_per_mtok']
        )
        line_items = {
            'Azure OpenAI generation or PTU': model_cost,
            'One-time corpus embedding amortized': embed_mtok * PRICES['embedding_3_large_per_mtok'] / 12,
            'Container Apps compute': avg_replicas * PRICES['containerapp_replica_month'],
            'PostgreSQL Flexible Server pgvector': PRICES[postgres_key],
            'Blob Storage audit and prompt registry': self.blob_gb * PRICES['blob_hot_gb_month'],
            'Azure Front Door Premium estimate': PRICES['frontdoor_month'],
            'Log Analytics ingest': workload.log_gb_per_day * 30 * PRICES['log_analytics_ingest_gb'],
            'Private Endpoints': private_endpoints * PRICES['private_endpoint_month'],
        }
        return {
            'workload': workload.label,
            'queries_month': int(queries_month),
            'billable_queries_after_cache': int(billable_queries),
            'raw_vector_gb': round(vector_gb_raw, 2),
            'line_items': {k: round(v, 2) for k, v in line_items.items()},
            'total': round(sum(line_items.values()), 2),
            'network_isolation_ok': self.private_networking and not self.public_egress_allowed,
        }

def insurance_topology() -> DeploymentTopology:
    return DeploymentTopology(
        name='insurance-underwriter-rag', region='eastus2',
        services=[
            Service(name='rag-api', sku='Azure Container Apps consumption'),
            Service(name='aoai', sku='Azure OpenAI gpt-4o + text-embedding-3-large'),
            Service(name='postgres', sku='Flexible Server General Purpose + pgvector'),
            Service(name='audit-blob', sku='StorageV2 hot immutable'),
            Service(name='key-vault', sku='standard'),
            Service(name='app-insights', sku='workspace-based'),
            Service(name='acr', sku='Premium'),
        ],
        prompt_registry_blob_url='https://stpromptprod.blob.core.windows.net/prompts/registry.json',
        vector_index_name='underwriting-index-2026-07-17',
        chat_model_deployment='gpt-4o-prod',
        embedding_model_deployment='text-embedding-3-large-prod',
    )

topology = insurance_topology()
scenarios = [
    Workload(label='Baseline', users=50, cache_hit_rate=0.10, log_gb_per_day=1.5),
    Workload(label='Growth', users=200, cache_hit_rate=0.20, use_ptu=True, log_gb_per_day=4.0),
    Workload(label='Enterprise', users=500, cache_hit_rate=0.25, use_ptu=True, log_gb_per_day=8.0),
]
for scenario in scenarios:
    report = topology.estimate_monthly_cost(scenario)
    print()
    print(f"{report['workload']} total=${report['total']:,.2f} queries={report['queries_month']:,} isolation={report['network_isolation_ok']}")
    for name, cost in report['line_items'].items():
        print(f"  {name:42s} ${cost:,.2f}")
```


Related: [[03 Permanent Notes/AI Week 20b Azure Enterprise AI Deployment Reference]]
