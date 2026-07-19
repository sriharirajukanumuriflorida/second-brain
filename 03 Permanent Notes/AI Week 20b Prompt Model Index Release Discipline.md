# AI Week 20b Prompt Model Index Release Discipline

Release every production AI behavior as a tuple: **`(prompt_version, model_deployment, index_version)`**.

- **Prompt lane**: prompt registry pointer, schema, few-shots, and guardrail text. Gate with golden-answer evals and online groundedness. Roll back by pointer from `prompt-vN` to `prompt-vN-1`.
- **Model lane**: Azure OpenAI deployment name and capacity choice, e.g. `gpt-4o-prod` to `gpt-4o-2024-11-prod`. Gate with latency, cost/query, refusal, and answer-quality metrics. Roll back traffic to the prior deployment.
- **Index lane**: shadow-built vector index plus metadata manifest. Gate with retrieval recall, citation coverage, and freshness checks. Roll back by alias to the previous warm index.

Never inline prompts in code or overwrite a live index in place. Canary at 10%, 50%, and 100%; monitor p95 latency, error rate, groundedness, citation coverage, and cost/query. When one axis fails, revert only that axis and preserve healthy changes.

> One-liner: **AI rollback must be axis-aware; otherwise every incident becomes a full-system rollback.**


Related: [[02 Literature Notes/AI Architecture/Cloud Architecture & Deployment — Applied]] · [[04 Code Snippets/AI Architecture/AI Week 20b Prompt Model Index Release Orchestrator]]
