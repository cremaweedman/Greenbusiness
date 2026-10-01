# GreenBusiness Backup / Restore Runbook

## Scope

Primary persistent state:
- PostgreSQL database;
- object storage under `STORAGE_BACKEND`;
- deployment environment/secrets stored outside the repository.

Redis is treated as transient and is not a backup source of truth.

## Backup

For the Docker development/alpha stack:

```bash
mkdir -p backups
docker compose exec -T postgres pg_dump \
  -U "${POSTGRES_USER:-greenbusiness}" \
  -d "${POSTGRES_DB:-greenbusiness}" \
  --format=custom \
  > "backups/greenbusiness-$(date +%Y%m%d-%H%M%S).dump"
```

If local object storage is in use, archive the mounted storage volume separately.

## Restore drill

Never test restores against the only copy of production data.

1. Stop application writers.
2. Create a fresh PostgreSQL database.
3. Restore the dump:
   ```bash
   pg_restore --clean --if-exists --no-owner --dbname=<restore-db> <backup.dump>
   ```
4. Run `alembic upgrade head`.
5. Verify:
   - user count;
   - wallet total;
   - ledger count;
   - latest migration revision;
   - active LiveOps version;
   - purchase ledger count.
6. Start the API against the restored DB.
7. Check `/health/ready` and a read-only player lookup.
8. Record the drill date and recovery result.

## Recovery objectives for closed alpha

Initial targets:
- RPO: 24 hours or better;
- RTO: 4 hours or better.

Tighten these only after measured operational need.

## Required production controls

Before closed alpha:
- scheduled encrypted DB backups;
- retention policy with at least daily + weekly recovery points;
- restore drill performed and documented;
- object-storage versioning or equivalent;
- backup credentials separate from runtime credentials.
