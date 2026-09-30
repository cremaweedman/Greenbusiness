# GreenBusiness

Canonical project repository for GreenBusiness.

## Canon

- [GREENBUSINESS_CANON_v1.1.zip](./GREENBUSINESS_CANON_v1.1.zip)
- [06_IMPLEMENTATION_ROADMAP.md](./06_IMPLEMENTATION_ROADMAP.md)
- [07_BUILD_HANDOFF.md](./07_BUILD_HANDOFF.md)
- [Phase 0 architecture](./docs/PHASE_0_ARCHITECTURE.md)

## Current development state

**Phase:** Phase 5 implementation started
**Milestone:** P5-M1 — LiveOps / Remote Config / Analytics / Admin Foundation — IN PROGRESS

## Requirements

- Docker
- Docker Compose

## Start

```bash
cp .env.example .env
docker compose up --build
```

Open:
- App: http://localhost:8080
- API liveness: http://localhost:8080/api/health/live
- API readiness: http://localhost:8080/api/health/ready
- API v1 ping: http://localhost:8080/api/v1/system/ping
- LiveOps config: http://localhost:8080/api/v1/liveops/config
- LiveOps experiment assignments: http://localhost:8080/api/v1/liveops/experiments
- Admin active config: http://localhost:8080/api/v1/admin/config/active
- Admin config history: http://localhost:8080/api/v1/admin/config/versions
- Admin ledger inspection: http://localhost:8080/api/v1/admin/ledger
- Admin economy dashboard: http://localhost:8080/api/v1/admin/dashboards/economy
- FastAPI docs: http://localhost:8080/api/docs

## Local web-only development

The web app can run directly on http://localhost:3000, but auth/gameplay still needs the API.

```bash
cd apps/web
npm install
npm run dev
```

By default, Next proxies `/api/*` to `http://localhost:8000`. Override it with `API_INTERNAL_URL` when the API is somewhere else.

## Migrations

```bash
docker compose exec api alembic upgrade head
```

## Tests

```bash
docker compose exec api pytest -q
docker compose exec api ruff check .
docker compose run --rm web npm run lint
docker compose run --rm web npm run typecheck
docker compose run --rm web npm test
```

## Object storage

Development defaults to the local persistent Docker volume:

```dotenv
STORAGE_BACKEND=local
STORAGE_LOCAL_PATH=/data/greenbusiness
```

Production can use any S3-compatible object store by setting `STORAGE_BACKEND=s3` plus the S3 environment variables in `.env.example`.

## Stop

```bash
docker compose down
```

Use `docker compose down -v` only when intentionally deleting local database and storage volumes.

Phase 0 through P4-M2 are complete and validated in CI. P5-M1 has started with versioned LiveOps config, admin-only publish/rollback, remote contract reward multipliers, deterministic experiment assignments, feature gates, analytics-event persistence, audited admin Cash grants/revokes, ledger inspection and first operational dashboard endpoints. Continue from `07_BUILD_HANDOFF.md`.
