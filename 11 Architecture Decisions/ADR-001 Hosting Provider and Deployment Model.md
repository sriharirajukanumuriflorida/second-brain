# ADR-001: Hosting Provider and Deployment Model

## Status
Approved

## Owner
Hari Kanumuri

## Date
2026-07-24

## Context
The FDE Vault Agent Platform requires cloud hosting for a FastAPI backend, React frontend, PostgreSQL database, and supporting infrastructure. The platform must be mobile-accessible, secure, and cost-controlled. Hosting decisions affect deployment complexity, operational overhead, cost predictability, and integration with other services (GitHub, monitoring, secrets management).

## Decision
**Primary Recommendation (Enterprise-Style): Azure**

- **Frontend:** Azure Static Web Apps
- **Backend:** Azure Container Apps or Azure App Service
- **Database:** Azure Database for PostgreSQL
- **Secrets:** Azure Key Vault
- **Monitoring:** Application Insights
- **CI/CD:** GitHub Actions

**Alternative (Personal Low-Friction):**

- **Frontend:** Vercel or Azure Static Web Apps
- **Backend:** Render, Fly.io, Railway, or Azure App Service
- **Database:** Managed PostgreSQL provider
- **Secrets:** Platform-managed environment secrets
- **Monitoring:** Platform logs plus structured app logs
- **CI/CD:** GitHub Actions

## Alternatives Considered

### AWS
- **Pros:** Mature services, extensive ecosystem
- **Cons:** Higher learning curve, potentially higher cost for small deployments

### GCP
- **Pros:** Strong Kubernetes support, good developer experience
- **Cons:** Less familiar integration with GitHub Actions compared to Azure

### Self-Hosted
- **Pros:** Maximum control, potential cost savings at scale
- **Cons:** High operational overhead, security burden, not aligned with MVP goals

## Consequences
- Platform will be cloud-hosted with clear separation of concerns
- Deployment strategy will use environment-based approach (dev/staging/production)
- Minimum MVP deployment: staging + production
- Main branch deploys to production only after review
- Pull requests deploy to preview/staging if supported
- Secrets must never be stored in source control
- Environment-specific configuration must be externalized

## Cost Impact
- Azure enterprise stack: predictable but potentially higher monthly cost
- Personal alternative: lower initial cost, pay-as-you-go pricing
- Cost categories to track: hosting, database, storage, monitoring/logging, bandwidth, secret management
- Budget enforcement required (see ADR-009)

## Security Impact
- Managed services reduce security burden
- Azure Key Vault provides secure secret management
- Application Insights provides security-relevant telemetry
- Platform-managed secrets reduce exposure risk
- Network security can be enforced through Azure networking features

## Operational Impact
- Azure provides integrated observability stack
- GitHub Actions integration is well-supported
- Disaster recovery procedures can leverage Azure backup features
- Platform redeployment is standardized through Azure deployment mechanisms
- Monitoring and alerting are centralized through Application Insights

## Follow-Up Actions
- [x] Select personal MVP stack (Cloudflare/Vercel + Render + Supabase)
- [ ] Create Cloudflare Pages or Vercel account
- [ ] Create Render account
- [ ] Create Supabase account
- [ ] Configure GitHub Actions for CI/CD
- [ ] Define environment-specific configuration strategy
- [ ] Validate disaster recovery procedures with selected providers
