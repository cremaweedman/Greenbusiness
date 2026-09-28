# GreenBusiness

Canonical project repository for GreenBusiness.

## Canon

- [GREENBUSINESS_CANON_v1.1.zip](./GREENBUSINESS_CANON_v1.1.zip)
- [06_IMPLEMENTATION_ROADMAP.md](./06_IMPLEMENTATION_ROADMAP.md)
- [07_BUILD_HANDOFF.md](./07_BUILD_HANDOFF.md)

## Current development state

**Phase:** Phase 0 — Foundation  
**Milestone:** P0-M1 — Repository & Production Foundation

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
- FastAPI docs: http://localhost:8080/api/docs

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

## Stop

```bash
docker compose down
```

Use `docker compose down -v` only when intentionally deleting the local database volume.

Continue from `07_BUILD_HANDOFF.md`; do not implement later phases early.
