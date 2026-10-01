# GreenBusiness

Canonical project repository for GreenBusiness.

## Canon

- [GREENBUSINESS_CANON_v1.1.zip](./GREENBUSINESS_CANON_v1.1.zip)
- [06_IMPLEMENTATION_ROADMAP.md](./06_IMPLEMENTATION_ROADMAP.md)
- [07_BUILD_HANDOFF.md](./07_BUILD_HANDOFF.md)
- [Phase 0 architecture](./docs/PHASE_0_ARCHITECTURE.md)

## Art production

- [Art Bible](./docs/canon/04_ART_BIBLE_AND_ASSET_SPEC_GREENBUSINESS_v1.0.md)
- [VS-01 Asset Manifest](./docs/canon/05_VS01_ASSET_MANIFEST_TEMPLATE.json)
- [3D art production pipeline](./docs/art/3D_PRODUCTION_PIPELINE_V1.md)
- [3D asset source-of-truth](./docs/art/3D_ASSET_SOURCE_OF_TRUTH.md)
- [Blender tooling](./tools/blender/README.md)

Structural art is authored as 3D-first and rendered to deterministic 2D runtime assets. GreenBusiness remains a web/PWA runtime; real-time 3D is not required for VS-01.

## Current development state

**Phase:** Phase 10 — Closed Alpha
**Milestone:** P10-3D-0 — interactive 3D Starter Room runtime spike under validation

## 3D runtime

GreenBusiness is now targeting a **3D Diorama Management Game** runtime:
- Next.js + React for management UI;
- Three.js + React Three Fiber for the interactive room;
- GLB/GLTF assets authored via Blender;
- FastAPI/Postgres/Redis remain server-authoritative.

See [3D Runtime Architecture](./docs/art/3D_RUNTIME_ARCHITECTURE_V1.md).

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

Phase 0 through P9-M1 are complete and validated. P10 technical alpha preparation is implemented on `feat/p10-m1-closed-alpha`: 10 varieties, compact skill trees, 40 decorations, alpha cohort/feedback/retention instrumentation and the first LiveOps mini-arc. The current branch has green CI and Security Scan. P10 remains open until real invited-cohort D1/D7, economy, club, reliability and feedback gates are measured. Continue from `07_BUILD_HANDOFF.md`.
