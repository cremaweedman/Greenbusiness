#!/usr/bin/env sh
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

: "${APP_ENV:=}"
: "${ALPHA_INSTANCE_ID:=}"
: "${ALPHA_RESET_CONFIRM:=}"

if [ "$APP_ENV" != "alpha" ]; then
  echo "REFUSED: APP_ENV must be exactly 'alpha'." >&2
  exit 2
fi

if [ -z "$ALPHA_INSTANCE_ID" ]; then
  echo "REFUSED: ALPHA_INSTANCE_ID is required." >&2
  exit 2
fi

case "$ALPHA_INSTANCE_ID" in
  *prod*|*production*|main|live)
    echo "REFUSED: ALPHA_INSTANCE_ID looks production-like: $ALPHA_INSTANCE_ID" >&2
    exit 2
    ;;
esac

EXPECTED="RESET_GREENBUSINESS_ALPHA:$ALPHA_INSTANCE_ID"
if [ "$ALPHA_RESET_CONFIRM" != "$EXPECTED" ]; then
  echo "REFUSED: ALPHA_RESET_CONFIRM must equal '$EXPECTED'." >&2
  exit 2
fi

echo "Resetting isolated GreenBusiness alpha instance: $ALPHA_INSTANCE_ID"

docker compose -f "$ROOT/docker-compose.yml" exec -T postgres psql   -v ON_ERROR_STOP=1   -U "${POSTGRES_USER:-greenbusiness}"   -d "${POSTGRES_DB:-greenbusiness}" <<'SQL'
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO PUBLIC;
SQL

docker compose -f "$ROOT/docker-compose.yml" exec -T api alembic upgrade head

echo "Alpha database reset complete."
echo "Next: run scripts/alpha_seed.sh to publish the canonical alpha LiveOps preset."
