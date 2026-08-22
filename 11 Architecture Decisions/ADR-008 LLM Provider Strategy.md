# ADR-008: LLM Provider Strategy

## Status
Approved

## Owner
Hari Kanumuri

## Date
2026-07-24

## Context
The FDE Vault Agent Platform uses LLMs for reasoning, synthesis, critique, architecture review, implementation planning, knowledge refresh analysis, and draft generation. The platform must support multiple LLM providers, handle provider failures gracefully, and externalize provider configuration for security and flexibility.

## Decision
**Provider Abstraction:**
- Implement provider abstraction layer
- Support multiple providers through common interface
- Provider configuration externalized and stored securely

**Supported Providers (Future):**
- Claude (Anthropic)
- Azure OpenAI
- OpenAI
- NASH LLM (enterprise/internal)
- Local models (Ollama, etc.)

**LLM Usage Rules:**
- Use LLMs only for: reasoning, synthesis, critique, architecture review, implementation planning, knowledge refresh analysis, draft generation
- Use deterministic code for: GitHub sync, folder scanning, Markdown parsing, YAML extraction, tag extraction, backlink extraction, file hash detection, search ranking, audit logs, cost logs, diff generation, pull request creation
- LLM must not be used as file parser, folder scanner, or metadata extractor

**Default Provider for MVP:**
- Claude or Azure OpenAI (selection deferred until Phase 3 when workflows begin)
- Claude recommended for general-purpose reasoning
- Azure OpenAI recommended if enterprise alignment required

**Phase Constraints:**
- Phase 0 (Foundation): No LLM usage
- Phase 1 (Backend Indexing): No LLM usage
- Phase 3 (Internal Knowledge Workflows): LLM usage begins

## Alternatives Considered

### Single Hardcoded Provider
- **Pros:** Simpler implementation
- **Cons:** Locked into one provider, cannot switch, rejected for flexibility

### LLM for Everything
- **Pros:** Unified approach
- **Cons:** Unnecessary cost, unreliable for deterministic operations, rejected per LLM usage rules

### Local Models Only
- **Pros:** No API cost, privacy
- **Cons:** Hardware requirements, model management, not suitable for all use cases

## Consequences
- Provider abstraction adds development overhead
- Provider switching requires no code changes
- Provider failures must be handled gracefully
- Provider secrets must be stored securely
- Cost tracking must be provider-agnostic
- Different providers may have different tokenization and pricing

## Cost Impact
- LLM cost tracked per provider, model, and workflow
- Provider selection affects per-token cost
- Budget enforcement required (see ADR-009)
- Local models have hardware cost instead of API cost

## Security Impact
- Provider secrets stored in secure secret management (Azure Key Vault or equivalent)
- No hardcoded API keys in source code
- Provider abstraction prevents provider-specific security issues
- LLM output is not trusted by default (human review required)

## Operational Impact
- Provider outages must be handled with fallback or retry
- Different providers may have different rate limits
- Cost tracking must normalize across providers
- Provider-specific features may not be available through abstraction
- Monitoring must track provider-specific metrics

## Follow-Up Actions
- [x] Define Phase 0/1 constraint: No LLM usage
- [x] Define default providers: Claude or Azure OpenAI (Phase 3+)
- [ ] Implement provider abstraction interface (Phase 3)
- [ ] Select default provider when workflows begin (Phase 3)
- [ ] Configure provider secrets in secret management (Phase 3)
- [ ] Implement provider-specific client implementations (Phase 3)
- [ ] Implement cost tracking per provider (Phase 3)
- [ ] Implement retry logic for provider failures (Phase 3)
- [ ] Test provider switching without code changes (Phase 3)
