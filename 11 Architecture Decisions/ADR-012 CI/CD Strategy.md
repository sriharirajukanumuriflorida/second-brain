# ADR-012: CI/CD Strategy

## Status
Approved

## Owner
Hari Kanumuri

## Date
2026-07-24

## Context
The FDE Vault Agent Platform requires automated deployment to staging and production environments. The CI/CD pipeline must ensure code quality through testing, security checks, and manual approval gates before production deployment. The pipeline must integrate with GitHub Actions given the GitHub-centric architecture.

## Decision
**CI/CD Pipeline (GitHub Actions):**

**Steps:**
1. Install dependencies
2. Run linting
3. Run unit tests
4. Run integration tests where possible
5. Build frontend
6. Build backend container
7. Run security checks where possible
8. Deploy to staging
9. Manual approval for production deployment
10. Deploy to production

**Deployment Strategy:**
- Environment-based: dev, staging, production
- Minimum MVP deployment: staging, production
- Main branch deploys to production only after review
- Pull requests deploy to preview/staging if supported
- Secrets must never be stored in source control
- Environment-specific configuration must be externalized

**Build Artifacts:**
- Frontend: Static build (React)
- Backend: Container image (FastAPI)
- Database migrations: Version-controlled migration files

**Quality Gates:**
- Unit tests must pass
- Integration tests must pass
- Linting must pass
- Security checks must pass (or be acknowledged)
- Manual approval required for production

## Alternatives Considered

### Manual Deployment
- **Pros:** Simple, no pipeline setup
- **Cons:** Error-prone, no quality gates, rejected per requirements

### No Staging Environment
- **Pros:** Simpler, lower cost
- **Cons:** Production bugs, no testing before release, rejected

### Direct Main Branch Deployment (No Approval)
- **Pros:** Faster deployment
- **Cons:** No review gate, risky, rejected per governance model

### Alternative CI/CD Tools (Jenkins, GitLab CI)
- **Pros:** Feature-rich alternatives
- **Cons:** GitHub Actions is native to GitHub ecosystem, chosen for integration

## Consequences
- All code changes go through CI/CD pipeline
- Production deployment requires manual approval
- Staging environment is required for testing
- Quality gates prevent broken deployments
- Deployment history is tracked in GitHub Actions
- Rollback capability must be supported

## Cost Impact
- GitHub Actions: Free tier sufficient for MVP
- Staging environment: additional hosting cost
- Build time: minimal cost impact
- No additional CI/CD tool licensing cost

## Security Impact
- Security checks in pipeline prevent vulnerable code
- Secrets never stored in source control
- Environment-specific configuration externalized
- Manual approval gate prevents unauthorized production changes
- Container scanning can detect vulnerabilities

## Operational Impact
- Automated deployment reduces manual errors
- Staging environment enables pre-production testing
- Quality gates improve code quality
- Manual approval provides control over production changes
- Pipeline failures block deployment until resolved
- Deployment history enables rollback decisions

## Follow-Up Actions
- [ ] Set up GitHub Actions workflow
- [ ] Configure staging and production environments
- [ ] Implement unit tests
- [ ] Implement integration tests
- [ ] Configure linting
- [ ] Configure security checks
- [ ] Set up manual approval gate for production
- [ ] Configure environment-specific configuration
- [ ] Test rollback procedure
- [ ] Document deployment process
