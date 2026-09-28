# GreenBusiness — Phase 0 Architecture

## Purpose

Phase 0 establishes the production foundation without implementing gameplay domain logic.

## Runtime topology

```text
Browser
  -> Nginx :8080
      -> Next.js web :3000
      -> FastAPI API :8000
          -> PostgreSQL
          -> ObjectStorage interface
              -> local filesystem in development
              -> S3-compatible provider in production
```

Redis remains intentionally unused until a measured requirement appears.

## API contracts

- Health endpoints remain unversioned:
  - `/health/live`
  - `/health/ready`
- Application endpoints are versioned under `/v1`.
- Expected application failures use the canonical envelope:

```json
{
  "error": {
    "code": "STABLE_MACHINE_CODE",
    "message": "Human-readable message.",
    "details": {},
    "request_id": "..."
  }
}
```

## Audit invariants

`audit_events` is append-only at the application layer. Events capture:
- event type;
- actor;
- optional target;
- request ID;
- structured payload;
- server timestamp.

Future domain writes should append an audit event inside the same database transaction when the action is security-, admin-, entitlement- or economy-relevant.

## Object storage

Application code depends on the `ObjectStorage` protocol, not directly on boto3.

Development:
- `STORAGE_BACKEND=local`
- files live under `STORAGE_LOCAL_PATH`.

Production:
- `STORAGE_BACKEND=s3`
- S3-compatible endpoint/bucket/credentials supplied through environment configuration.

## Database

- PostgreSQL is the source of truth.
- Alembic is the only schema migration mechanism.
- Async SQLAlchemy sessions are used by application services.
- CI includes a real PostgreSQL migration + integration test.

## Security baseline

CI blocks:
- Python dependency vulnerabilities reported by `pip-audit`;
- npm vulnerabilities at high/critical severity;
- backend/frontend lint/test/build failures;
- Docker full-stack smoke failures.

No secrets are committed.
