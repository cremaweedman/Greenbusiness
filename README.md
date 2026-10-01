# GreenBusiness

Canonical project repository for GreenBusiness.

## Canon

- [GREENBUSINESS_CANON_v1.1.zip](./GREENBUSINESS_CANON_v1.1.zip)
- [06_IMPLEMENTATION_ROADMAP.md](./06_IMPLEMENTATION_ROADMAP.md)
- [07_BUILD_HANDOFF.md](./07_BUILD_HANDOFF.md)
- [Phase 0 architecture](./docs/PHASE_0_ARCHITECTURE.md)

## Current development state

**Phase:** Phase 9 complete — Phase 10 ready
**Milestone:** P10-M1 — Content Completion & Closed Alpha — READY, NOT STARTED

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
- Social state: http://localhost:8080/api/v1/social/me
- Store catalog: http://localhost:8080/api/v1/store/catalog
- Notification state: http://localhost:8080/api/v1/notifications/me
- Platform readiness: http://localhost:8080/api/v1/platform/readiness
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

Phase 0 through P9-M1 are complete and validated. P9 hardened production defaults, sandbox monetization, admin auth/RBAC, rate limiting, security headers, encrypted push tokens, replay/exploit logging, LiveOps concurrency, social transactions, container/runtime security, backup/restore and security scanning. The repository is intentionally stopped before P10 Closed Alpha. Continue from `07_BUILD_HANDOFF.md`.
