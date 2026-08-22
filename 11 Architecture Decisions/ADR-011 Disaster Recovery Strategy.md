# ADR-011: Disaster Recovery Strategy

## Status
Approved

## Owner
Hari Kanumuri

## Date
2026-07-24

## Context
The FDE Vault Agent Platform has recoverable state beyond the GitHub vault: database records, workflow history, cost logs, audit logs, configuration, and cache metadata. The vault itself is protected by GitHub, but the platform database and configuration require backup and recovery procedures. The vector index is rebuildable and must not be treated as the system of record.

## Decision
**Recovery Objectives (MVP):**
- Recovery Time Objective (RTO): 4 hours
- Recovery Point Objective (RPO): 24 hours

**Critical Recovery Assets:**
- Private GitHub vault repository
- Application database backup
- Environment configuration
- Secrets and key references
- Deployment pipeline
- Workflow audit logs
- Cost logs

**DR Test Procedure:**
Run before production launch and then at least quarterly:
1. Export or verify latest application database backup
2. Simulate database loss in staging
3. Restore database from backup
4. Rebuild backend working copy from GitHub
5. Rebuild keyword search index
6. Rebuild vector index if enabled
7. Verify workflow history is restored
8. Verify cost logs are restored
9. Verify audit logs are restored
10. Verify user login works
11. Verify vault search works
12. Verify a workflow can run in staging
13. Verify no generated PR references are lost
14. Document recovery duration and issues

**Vault Recovery:**
- Vault is protected by GitHub (primary protection)
- GitHub repository rollback if needed
- Backend working copy is disposable and can be rebuilt from GitHub
- No separate vault backup required (GitHub is the backup)

**Index Recovery:**
- Keyword search index can be rebuilt from vault
- Vector index can be rebuilt from vault (cost consideration)
- Indexes are not treated as system of record

## Alternatives Considered

### No DR Strategy
- **Pros:** No overhead
- **Cons:** Catastrophic data loss risk, rejected per requirements

### Vault-Only Recovery (No Database Backup)
- **Pros:** Simpler
- **Cons:** Loss of workflow history, cost logs, audit records, rejected

### Real-Time Replication
- **Pros:** Near-zero RPO
- **Cons:** Complexity, cost, overkill for MVP, rejected

## Consequences
- Database backups are mandatory
- DR testing is required quarterly
- Recovery procedures must be documented
- Vector index is rebuildable (not backed up)
- GitHub is primary vault protection
- RTO/RPO targets must be met

## Cost Impact
- Database backup cost (provider-dependent)
- Storage cost for backup retention
- DR testing requires staging environment
- No additional cost for GitHub-based vault protection

## Security Impact
- Backups must be encrypted
- Backup access must be restricted
- Secrets must be recoverable without exposure
- Audit logs must be preserved for security investigations

## Operational Impact
- DR testing requires quarterly time investment
- Recovery procedures must be kept up-to-date
- Backup retention policies must be defined
- Recovery duration must be measured and tracked
- Staff must be trained on recovery procedures

## Follow-Up Actions
- [ ] Configure automated database backups
- [ ] Define backup retention policy
- [ ] Document recovery procedures
- [ ] Schedule quarterly DR tests
- [ ] Implement index rebuild procedures
- [ ] Verify GitHub repository protection
- [ ] Train staff on recovery procedures
- [ ] Measure and document RTO/RPO compliance
