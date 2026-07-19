# Retries Need Jitter and Idempotency

Retries help only when failures are transient and the repeated operation is safe. Exponential backoff prevents immediate hammering; jitter prevents every client from retrying in synchronized waves; caps prevent runaway latency and cost. If a retry can cause side effects, use an idempotency key so repeated attempts collapse into one logical action.

Without jitter, retries amplify outages. Without idempotency, retries duplicate reality.

> One-liner: **retry only what is safe, staggered, and bounded.**


Related: [[02 Literature Notes/LLM Engineering/Reliability Patterns]] · [[02 Literature Notes/LLM Engineering/Cost Architecture]]
