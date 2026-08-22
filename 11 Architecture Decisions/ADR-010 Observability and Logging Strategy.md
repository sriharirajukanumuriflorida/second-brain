# ADR-010: Observability and Logging Strategy

## Status
Approved

## Owner
Hari Kanumuri

## Date
2026-07-24

## Context
The FDE Vault Agent Platform requires observability to troubleshoot sync failures, workflow failures, LLM cost spikes, authentication issues, GitHub API failures, and deployment problems. The platform must be observable enough to operate reliably while avoiding exposure of sensitive data.

## Decision
**Selected Observability Stack (Personal/Non-Azure):**
- Application logs: Structured JSON logs
- Error tracking: Sentry (optional)
- Uptime checks: Better Stack, UptimeRobot, or provider health checks
- Metrics: Provider-native metrics (Render, Supabase, Cloudflare/Vercel)
- CI/CD logs: GitHub Actions logs
- Database metrics: Supabase dashboard
- Structured application logs: JSON logs emitted by backend

**Required Log Events:**
```text
auth.login_success
auth.login_failed
auth.logout
vault.sync_started
vault.sync_completed
vault.sync_failed
index.scan_started
index.scan_completed
index.scan_failed
search.query_executed
workflow.started
workflow.retrieval_completed
workflow.llm_started
workflow.llm_failed
workflow.draft_generated
workflow.approved
workflow.rejected
github.branch_created
github.pr_created
github.pr_failed
cost.estimated
cost.budget_warning
rate_limit.exceeded
```

**Logging Rules:**
- Do not log secrets
- Do not log access tokens
- Do not log full sensitive note content
- Log note IDs, paths, hashes, and source references where needed
- Use correlation IDs for workflow runs
- Use structured JSON logs

**Minimum Alerting Rules:**
- Trigger alert on repeated login failures
- Trigger alert on workflow failure rate spike
- Trigger alert on GitHub sync failure
- Trigger alert on budget threshold crossing at 80% and 100%
- Trigger alert on backend 5xx error spike
- Trigger alert on database connectivity failure

## Alternatives Considered

### No Structured Logging
- **Pros:** Simpler implementation
- **Cons:** Unparseable logs, poor observability, rejected

### Log Everything Including Sensitive Content
- **Pros:** Complete visibility
- **Cons:** Security risk, compliance issues, rejected

### No Alerting
- **Pros:** Simpler implementation
- **Cons:** No proactive issue detection, rejected per operational requirements

## Consequences
- All logs are structured JSON for parsing
- Sensitive data is excluded from logs
- Correlation IDs enable workflow tracing
- Alerting provides proactive issue detection
- Observability stack depends on hosting provider choice (ADR-001)
- Logs support troubleshooting and audit requirements

## Cost Impact
- Azure Application Insights: cost based on data volume
- Sentry: cost based on events and volume
- Uptime monitoring: minimal cost
- Log volume must be managed to control costs

## Security Impact
- No secrets or tokens in logs
- No full note content in logs
- Note IDs and hashes are safe to log
- Structured logs enable security event correlation
- Secrets audit trail from Key Vault

## Operational Impact
- Structured logs enable automated parsing and alerting
- Correlation IDs simplify troubleshooting
- Alerting enables proactive issue resolution
- Observability stack choice affects implementation
- Log retention policies must be defined

## Follow-Up Actions
- [ ] Select observability stack based on ADR-001 decision
- [ ] Implement structured JSON logging
- [ ] Implement correlation ID generation
- [ ] Implement required log events
- [ ] Configure alerting rules
- [ ] Implement log exclusion for sensitive data
- [ ] Set up log retention policies
- [ ] Test alerting for critical events
