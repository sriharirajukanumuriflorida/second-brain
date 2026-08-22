# Deployment Guide - FDE Vault Agent Platform

## Overview

This guide covers deploying the FDE Vault Agent Platform to production using:
- **Backend**: Render (Python/FastAPI)
- **Frontend**: Vercel (React/Vite)
- **Database**: Supabase PostgreSQL
- **CI/CD**: GitHub Actions

## Prerequisites

### 1. Supabase Setup

1. Create a Supabase project at https://supabase.com
2. Enable pgvector extension in SQL Editor:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. Get your database connection string from Settings → Database
4. Save connection string for Render configuration

### 2. GitHub OAuth Setup

1. Go to GitHub Settings → Developer settings → OAuth Apps
2. Create new OAuth App:
   - Application name: "FDE Vault Agent Platform"
   - Homepage URL: `https://your-frontend-url.vercel.app`
   - Authorization callback URL: `https://your-frontend-url.vercel.app/auth/callback`
3. Copy Client ID and Client Secret
4. Add to Render environment variables

### 3. Render Setup

1. Create account at https://render.com
2. Connect your GitHub repository
3. Create new Web Service:
   - Name: `fde-vault-backend`
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Create PostgreSQL database:
   - Name: `fde-vault-db`
   - Use Supabase connection string
5. Add environment variables:
   - `DATABASE_URL`: (from Supabase)
   - `LLM_PROVIDER`: `anthropic`
   - `LLM_API_KEY`: (your Anthropic API key)
   - `LLM_MODEL`: `claude-3-5-sonnet-20241022`
   - `EMBEDDING_PROVIDER`: `openai`
   - `EMBEDDING_API_KEY`: (your OpenAI API key)
   - `EMBEDDING_MODEL`: `text-embedding-3-small`
   - `GITHUB_PAT`: (your GitHub Personal Access Token)
   - `GITHUB_OAUTH_CLIENT_ID`: (from GitHub OAuth App)
   - `GITHUB_OAUTH_CLIENT_SECRET`: (from GitHub OAuth App)
   - `GITHUB_OAUTH_REDIRECT_URI`: `https://your-frontend-url.vercel.app/auth/callback`
   - `VAULT_PATH`: `/opt/vault`

### 4. Vercel Setup

1. Create account at https://vercel.com
2. Import your GitHub repository
3. Configure:
   - Framework Preset: Vite
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. Add environment variable:
   - `VITE_API_URL`: `https://your-backend-url.onrender.com`
5. Deploy

### 5. GitHub Actions Setup

1. Go to your repository Settings → Secrets and variables → Actions
2. Add secrets:
   - `RENDER_API_KEY`: (from Render Account Settings)
   - `RENDER_SERVICE_ID`: (from Render dashboard)
   - `VERCEL_TOKEN`: (from Vercel account settings)
   - `VERCEL_ORG_ID`: (from Vercel project settings)
   - `VERCEL_PROJECT_ID`: (from Vercel project settings)
3. Enable GitHub Actions in repository settings

## Database Migration

After deployment, run database migrations in Supabase SQL Editor:

```sql
-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Create tables (SQLAlchemy will create most, but add custom indexes as needed)
-- Tables are auto-created by SQLAlchemy on first run
```

## Monitoring

- **Health Check**: `https://your-backend-url.onrender.com/api/v1/health`
- **Metrics**: `https://your-backend-url.onrender.com/api/v1/metrics`
- **Logs**: Render Dashboard → Logs
- **Database**: Supabase Dashboard → Database

## Backup Strategy

### Database Backups
- Supabase provides automatic daily backups
- Enable point-in-time recovery in Supabase settings

### Vault Backup
- Vault should be backed up separately (git repository)
- Consider using GitHub for vault storage with automatic sync

## Security Hardening

### Production CORS
Update CORS configuration in `main.py`:
```python
allow_origins=[
    "https://your-frontend-url.vercel.app"
]
```

### Rate Limiting
Rate limiting is enabled using slowapi. Adjust limits as needed in `security.py`.

### Secrets Management
- Never commit secrets to repository
- Use environment variables for all sensitive data
- Rotate API keys regularly

## Troubleshooting

### Backend won't start
- Check Render logs for errors
- Verify environment variables are set
- Ensure database connection string is correct

### Frontend can't connect to backend
- Verify `VITE_API_URL` is correct
- Check CORS configuration
- Ensure backend is running

### GitHub OAuth failing
- Verify callback URL matches exactly
- Check Client ID and Secret are correct
- Ensure OAuth App is not in development mode

## Rollback Procedure

### Backend Rollback
1. Go to Render dashboard
2. Deploy previous commit
3. Or revert commit in GitHub and let CI/CD redeploy

### Frontend Rollback
1. Go to Vercel dashboard
2. Deploy previous deployment
3. Or revert commit in GitHub and let CI/CD redeploy

## Cost Estimates

- **Render**: Free tier available (up to 750 hours/month)
- **Vercel**: Free tier available (up to 100GB bandwidth/month)
- **Supabase**: Free tier available (500MB database)
- **LLM Costs**: Variable based on usage (monitor via cost tracking)
