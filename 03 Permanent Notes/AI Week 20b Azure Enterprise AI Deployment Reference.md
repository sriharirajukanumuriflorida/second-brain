# AI Week 20b Azure Enterprise AI Deployment Reference

Reusable Azure deployment reference for the insurance-underwriter RAG assistant pattern:

1. **Ingress and compute**: Azure Front Door Premium + WAF into Azure Container Apps hosting the FastAPI RAG service, with revisions and traffic splitting.
2. **Model and retrieval**: Azure OpenAI `gpt-4o` and `text-embedding-3-large` in an approved region; Azure Database for PostgreSQL Flexible Server with `pgvector` for chunks, metadata, and eval results.
3. **Audit and config**: Blob Storage with immutability for audit events; Blob/Git-backed prompt registry and index manifests.
4. **Identity and secrets**: Entra ID for users; managed identity for workload; Key Vault for secrets, certs, and optional CMK.
5. **Networking**: Private Endpoints and private DNS for OpenAI, Postgres, Blob, Key Vault, ACR, and telemetry where supported; deny arbitrary public egress.
6. **Observability and cost**: Application Insights/OpenTelemetry for traces and groundedness metrics; Blob for full audit; sampled Log Analytics to control cost and PII scope.
7. **IaC and release**: Bicep modules with environment parameter files; CI/CD gates for tests, evals, image scan, staging revision, smoke tests, canary, and rollback.

> One-liner: **an enterprise AI deployment is a private, observable, parameterized Azure system — not a model endpoint with a web app attached.**


Related: [[02 Literature Notes/AI Architecture/Cloud Architecture & Deployment — Applied]] · [[04 Code Snippets/AI Architecture/AI Week 20b Azure Deployment Topology Cost Estimator]]
