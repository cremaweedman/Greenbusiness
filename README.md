# GreenBusiness

Canonical project repository for GreenBusiness.

## Canon

- [GREENBUSINESS_CANON_v1.1.zip](./GREENBUSINESS_CANON_v1.1.zip)
- [06_IMPLEMENTATION_ROADMAP.md](./06_IMPLEMENTATION_ROADMAP.md)
- [07_BUILD_HANDOFF.md](./07_BUILD_HANDOFF.md)
- [Phase 0 architecture](./docs/PHASE_0_ARCHITECTURE.md)

## Current development state

**Phase:** Phase 3 implementation started  
**Milestone:** P3-M1 — Contracts/economy base in progress; P2-M1 still pending Docker E2E validation

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
- Contracts: http://localhost:8080/api/v1/contracts
- Cash ledger: http://localhost:8080/api/v1/economy/cash-ledger
- Economy summary: http://localhost:8080/api/v1/economy/summary
- Upgrades: http://localhost:8080/api/v1/upgrades
- Skills: http://localhost:8080/api/v1/skills
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

Phase 0 and P1-M1 are complete. P2-M1 has been implemented on the production-loop slice and should be validated with the Docker-based backend/frontend/full-stack checks before it is marked complete. P3-M1 has started with versioned starter contracts, active contract boards, Cash-priced rerolls, Cash/Reputation rewards, a Cash ledger base, contract delivery UI, player-visible Cash history, a source/sink economy summary, starter Cash sink upgrades for yield and slot capacity, a 20-level progression curve with skill-point awards, starter Botany/Commerce/Operations skills with respec, and integration coverage prepared for Docker/PostgreSQL validation.
