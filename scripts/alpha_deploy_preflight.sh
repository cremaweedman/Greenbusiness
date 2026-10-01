#!/usr/bin/env sh
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="${ALPHA_ENV_FILE:-$ROOT/.env.alpha}"

if [ ! -f "$ENV_FILE" ]; then
  echo "Missing alpha env file: $ENV_FILE" >&2
  exit 2
fi

set -a
. "$ENV_FILE"
set +a

if [ "${APP_ENV:-}" != "alpha" ]; then
  echo "REFUSED: APP_ENV must equal alpha." >&2
  exit 2
fi

for name in POSTGRES_DB POSTGRES_USER POSTGRES_PASSWORD DATABASE_URL JWT_SECRET ADMIN_API_KEY ADMIN_JWT_SECRET ADMIN_ACTOR_ID PUSH_TOKEN_ENCRYPTION_KEY; do
  eval "value=\${$name:-}"
  if [ -z "$value" ]; then
    echo "Missing required variable: $name" >&2
    exit 2
  fi
done

case "$POSTGRES_PASSWORD$JWT_SECRET$ADMIN_API_KEY$ADMIN_JWT_SECRET" in
  *change-me*|*replace-with*)
    echo "REFUSED: placeholder secrets remain in alpha env." >&2
    exit 2
    ;;
esac

docker compose   --env-file "$ENV_FILE"   -f "$ROOT/docker-compose.yml"   -f "$ROOT/docker-compose.alpha.yml"   config >/dev/null

echo "Alpha deployment preflight passed."
