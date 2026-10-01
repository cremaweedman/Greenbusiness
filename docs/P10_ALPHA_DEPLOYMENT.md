# P10 Alpha Deployment

This deployment layer is provider-neutral and targets a single isolated Docker host for Closed Alpha.

## Topology

Internet/TLS proxy -> localhost:${ALPHA_HTTP_PORT:-8080} -> Nginx -> Web/API

PostgreSQL and Redis are internal-only Docker services. They are not published to the host.

## Files

- `docker-compose.alpha.yml` — secure alpha override;
- `.env.alpha.example` — alpha-only environment template;
- `scripts/alpha_deploy_preflight.sh` — rejects placeholders/missing security values;
- `scripts/alpha_deploy.sh` — build, migrate, start and smoke-test;
- `scripts/alpha_rollback.sh` — code rollback guidance without unsafe automatic DB downgrade.

## First deployment

```bash
cp .env.alpha.example .env.alpha
# replace every secret/hostname placeholder
./scripts/alpha_deploy_preflight.sh
./scripts/alpha_deploy.sh
```

Then terminate HTTPS outside the Compose stack with a managed load balancer, Caddy, Traefik, Cloudflare Tunnel, or equivalent. The bundled Nginx listens only on localhost in alpha.

## After first clean deploy

Only for the isolated alpha database:

```bash
export APP_ENV=alpha
export ALPHA_INSTANCE_ID=gb-alpha-eu1
export ALPHA_RESET_CONFIRM="RESET_GREENBUSINESS_ALPHA:$ALPHA_INSTANCE_ID"
./scripts/alpha_reset.sh

export ADMIN_API_KEY="<same alpha admin key>"
export ALPHA_BASE_URL="https://alpha.example.com"
./scripts/alpha_seed.sh
```

Do not run `alpha_reset.sh` after real cohort data exists unless the wave is intentionally being discarded.

## Release procedure

1. merge validated code to `main`;
2. create a Git tag or record the exact SHA;
3. take a database backup if alpha contains real tester data;
4. pull that exact SHA on the alpha host;
5. run `alpha_deploy_preflight.sh`;
6. run `alpha_deploy.sh`;
7. confirm public HTTPS health/readiness;
8. record deployed SHA + active LiveOps config version.

## Rollback

Code rollback may use a previously green SHA. Database migrations are forward-only by default during alpha. Do not automatically run Alembic downgrade against tester data.

## Backup rule

Once Wave 1 starts, create a backup before each deployment that includes schema migrations or economy changes.
