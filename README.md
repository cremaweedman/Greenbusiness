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
- [2D/2.5D runtime architecture](./docs/art/2D_RUNTIME_ARCHITECTURE_V1.md)
- [Mobile-first UX](./docs/MOBILE_FIRST_UX_V1.md)
- [Master Asset Catalog](./docs/art/MASTER_ASSET_CATALOG_V1.md)
- [Concept Art Master List](./docs/art/CONCEPT_ART_MASTER_LIST_V1.md)
- [Machine-readable Asset Prompts](./art/prompts/MASTER_ASSET_PROMPTS_V1.json)
- [Blender tooling](./tools/blender/README.md)
- [Asset Factory](./tools/asset_factory/README.md)

Structural art is authored 3D-first where useful, then rendered to deterministic 2D/2.5D isometric runtime assets. GreenBusiness remains a web/PWA management game; real-time 3D is explicitly not the primary gameplay renderer.

## Current development state

**Phase:** Phase 10 — Closed Alpha
**Milestone:** P10-ART-2 — Starter Crops production

## Runtime presentation — canonical

GreenBusiness targets a **premium mobile-first 2D/2.5D isometric management-game runtime**:
- Next.js + React for the gameplay UI and scene composition;
- layered WebP/AVIF/SVG assets for the interactive room;
- Blender/Meshy/Tripo may be used upstream to author consistent 3D masters;
- approved 3D masters are rendered to deterministic isometric runtime states;
- CSS/Canvas/Web Animations may provide lightweight particles, highlights and transitions;
- Three.js / React Three Fiber are non-canonical experiments and must not become a dependency of the core gameplay loop without a new explicit architecture decision;
- FastAPI/Postgres/Redis remain server-authoritative.
- Primary gameplay target: mobile portrait (390×844 baseline, 360–430 px width test range).
- Mobile uses bottom navigation + contextual bottom sheets; persistent desktop sidebars are non-canonical.

See [2D/2.5D Runtime Architecture](./docs/art/2D_RUNTIME_ARCHITECTURE_V1.md). The former [3D Runtime Architecture](./docs/art/3D_RUNTIME_ARCHITECTURE_V1.md) is superseded.

## Art status

- P0 concept-art lock: 15/15 approved.
- P10-ART-1 Starter Room: COMPLETE — layered 2D/2.5D runtime, modular room assets, interactive slots, mobile bottom sheet/navigation and automated payload gate are merged.
- Starter Slot / Slot States: approved.
- Starter crop family (Aurora Drift / Ember Leaf / Moon Sprout): approved.
- Character style + mobile UI direction: approved.
- Next execution target: P10-ART-2 production-ready Aurora Drift / Ember Leaf / Moon Sprout assets and in-room integration.

## Asset Factory

The canonical 93-asset catalog can be processed reproducibly through the Asset Factory. ART-2 is defined as 3 starter crops × 3 states × 4 candidates = 36 deterministic generation jobs.

```bash
python tools/asset_factory/factory.py validate --batch P10-ART-2
python tools/asset_factory/factory.py prepare --batch P10-ART-2
```

See [Asset Factory](./tools/asset_factory/README.md).

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
