# AI Week 20a Cloud AI Platform Decision Guide

Use this guide when a customer asks which managed AI platform should host an enterprise AI workload.

1. **Start with residency and procurement**. If the customer already has Azure landing zones, Entra ID governance, Private Link standards, Microsoft DPA coverage, and approved Azure regions, Azure AI Foundry / Azure OpenAI is the default. If AWS or Google is the governed estate, Bedrock or Vertex AI may reduce review time more than any model benchmark advantage.
2. **Compare model catalog with evals, not logos**. Azure OpenAI gives OpenAI models through Azure controls; Bedrock gives Anthropic, Titan, Cohere, Meta, Mistral, and others; Vertex AI Model Garden gives Gemini plus third-party/open models.
3. **Capacity is a product decision**. Standard/on-demand works for pilots and bursty use; Azure OpenAI PTU, Bedrock Provisioned Throughput, or provisioned Vertex endpoints are for predictable SLOs and steady utilization. Idle reservations are real money.
4. **Private networking and keys matter**. Prefer private endpoints/VPC endpoints, managed identity/workload identity, customer-managed key options where required, and auditable secret rotation.
5. **Keep an escape hatch**. Hide provider SDKs behind a provider port so procurement, region availability, quota, or model-quality changes do not rewrite product logic.

> One-liner: **pick the platform whose model quality, approved regions, private path, quota story, and commercial terms the customer can operate — then abstract it behind a port.**


Related: [[02 Literature Notes/AI Architecture/Cloud Architecture & Deployment — Reference Patterns]] · [[04 Code Snippets/AI Architecture/AI Week 20a Canary Release Evaluator]]
