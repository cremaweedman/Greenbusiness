# GreenBusiness

Canonical project repository for GreenBusiness.

## Canon

- [GREENBUSINESS_CANON_v1.1.zip](./GREENBUSINESS_CANON_v1.1.zip)
- [06_IMPLEMENTATION_ROADMAP.md](./06_IMPLEMENTATION_ROADMAP.md)
- [07_BUILD_HANDOFF.md](./07_BUILD_HANDOFF.md)
- [Phase 0 architecture](./docs/PHASE_0_ARCHITECTURE.md)

## Current development state

**Phase:** Phase 7 ready
**Milestone:** P7-M1 — Monetization & Entitlements — READY, NOT STARTED

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

Phase 0 through P6-M1 are complete and validated. P6-M1 delivered the own social graph, friend codes/deep-link payloads, club lifecycle, invites, structured reactions, weekly club objectives, idempotent contribution ledger, limited assists, club rewards, anti-abuse limits and an independent LiveOps `clubs` feature flag. Continue from `07_BUILD_HANDOFF.md`.
