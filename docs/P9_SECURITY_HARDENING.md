# GreenBusiness P9 Security Hardening

## Runtime rules

Production-like environments are `production`, `prod`, and `staging`.

The API refuses to start in those environments unless:
- `JWT_SECRET` is strong and non-default;
- `ADMIN_API_KEY` is at least 32 characters;
- `ADMIN_JWT_SECRET` is at least 32 characters and different from `JWT_SECRET`;
- `COOKIE_SECURE=true`;
- creator access is disabled;
- sandbox monetization and rewarded-ad claims are disabled;
- Redis-backed rate limiting is enabled;
- `PUSH_TOKEN_ENCRYPTION_KEY` is explicitly configured.

## Admin boundary

`X-Admin-Key` is a bootstrap credential only. Use it against:

`POST /v1/admin/auth/token`

The resulting short-lived admin JWT carries an actor id and role.

Roles:
- `viewer`: read-only admin access;
- `operator`: config and economy mutations;
- `superadmin`: full current admin scope.

Direct `X-Admin-Key` access to protected admin routes is only accepted in development/local/test for compatibility.

## Sandbox isolation

The sandbox purchase validator and sandbox rewarded-ad grants are available only when:
- the application environment is development/local/test; and
- the corresponding explicit sandbox feature flag is enabled.

Production providers are fail-closed until a real provider adapter is implemented.

## Rate limiting

Sensitive auth, admin, store, social and club paths are rate-limited.

Development/test can use the in-memory backend.
Production-like environments require Redis.

## HTTP hardening

The API and Nginx add:
- CSP;
- frame denial;
- no-sniff;
- referrer policy;
- permissions policy;
- HSTS in production-like API responses.

## Push token storage

Push tokens are no longer stored only as hashes. New registrations retain:
- SHA-256 hash for deduplication;
- non-secret label for display;
- Fernet-encrypted ciphertext for future provider delivery.

Existing pre-P9 rows without ciphertext remain readable as registry entries but cannot be used for delivery until refreshed.

## LiveOps concurrency

LiveOps version allocation uses a PostgreSQL advisory transaction lock before `MAX(version)+1`, preventing concurrent publishers from racing.

## Security event logging

Exploit/replay/rate-limit events use the `greenbusiness.security` logger and intentionally omit credentials, cookies, raw tokens and receipt ids.
