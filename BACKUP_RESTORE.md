# Backup and Restore Procedures

## Database Backup

### Automatic Backups (Supabase)
- Supabase provides automatic daily backups (retained for 7 days on free tier)
- Enable in Supabase Dashboard → Database → Backups
- Point-in-time recovery available (up to 7 days)

### Manual Database Export
```bash
# Export database to SQL
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Export schema only
pg_dump --schema-only $DATABASE_URL > schema_backup.sql

# Export data only
pg_dump --data-only $DATABASE_URL > data_backup.sql
```

### Manual Database Import
```bash
# Restore from SQL backup
psql $DATABASE_URL < backup_20240101.sql
```

## Vault Backup

### Git-Based Backup
Vault should be stored in a git repository for version control and backup:

```bash
# Commit vault changes
cd vault_clone
git add .
git commit -m "Backup $(date)"
git push origin main
```

### Automated Vault Backup Script
Create `scripts/backup_vault.sh`:
```bash
#!/bin/bash
cd /path/to/vault_clone
git add .
git commit -m "Automated backup $(date)"
git push origin main
```

Add to cron job:
```bash
# Daily backup at 2 AM
0 2 * * * /path/to/scripts/backup_vault.sh
```

## Embedding Backup

Embeddings are stored in the database and included in database backups.

To re-generate embeddings if needed:
```bash
curl -X POST http://localhost:8000/api/v1/embeddings/generate \
  -H "Content-Type: application/json" \
  -d '{"note_id": 1}'
```

## Configuration Backup

### Environment Variables
Export environment variables to a secure file:
```bash
# Export to encrypted file (using gpg)
printenv | grep -E "LLM|GITHUB|DATABASE|EMBEDDING" | gpg -e > env_backup.gpg

# Restore
gpg -d env_backup.gpg > .env
```

### Configuration Files
Backup configuration files:
- `backend/.env`
- `backend/app/config.py`
- `frontend/.env`

## Restore Procedure

### Full System Restore

1. **Restore Database**
   ```bash
   # From Supabase backup (via dashboard)
   # Or from manual backup
   psql $DATABASE_URL < backup_20240101.sql
   ```

2. **Restore Vault**
   ```bash
   git clone your-vault-repo
   ```

3. **Restore Configuration**
   ```bash
   gpg -d env_backup.gpg > backend/.env
   ```

4. **Restart Services**
   - Render: Deploy new build
   - Vercel: Deploy new build

### Partial Restore

#### Notes Only
```bash
# Restore notes from git
cd vault_clone
git checkout <commit-hash>
```

#### Embeddings Only
```bash
# Re-embed all notes
curl -X POST http://localhost:8000/api/v1/embeddings/re-embed \
  -H "Content-Type: application/json"
```

#### Users Only
```sql
-- Restore users from backup
-- (This requires manual SQL intervention)
```

## Disaster Recovery

### Scenario: Database Corruption
1. Restore from latest Supabase backup
2. Verify data integrity
3. Re-run any failed operations

### Scenario: Vault Loss
1. Clone vault from git repository
2. Sync with backend
3. Re-generate embeddings if needed

### Scenario: Configuration Loss
1. Restore from encrypted backup
2. Update environment variables in Render
3. Redeploy

## Testing Backups

### Monthly Backup Test
1. Test restore to staging environment
2. Verify data integrity
3. Document any issues
4. Update procedures as needed

### Backup Verification Script
```python
# scripts/verify_backup.py
import requests

def verify_backup():
    # Check database connectivity
    # Verify note count
    # Check embedding status
    # Verify user accounts
    pass
```

## Retention Policy

- **Database**: 7 days (Supabase free tier), 30 days (paid)
- **Vault**: Indefinite (git history)
- **Configuration**: Indefinite (encrypted)
- **Logs**: 7 days (Render), 30 days (Vercel)

## Compliance

- Ensure backups comply with data retention policies
- Encrypt sensitive backups
- Store backups in secure location
- Document backup access controls
