#!/usr/bin/env sh
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="${ALPHA_ENV_FILE:-$ROOT/.env.alpha}"

ALPHA_ENV_FILE="$ENV_FILE" "$ROOT/scripts/alpha_deploy_preflight.sh"

set -a
. "$ENV_FILE"
set +a

COMPOSE="docker compose --env-file $ENV_FILE -f $ROOT/docker-compose.yml -f $ROOT/docker-compose.alpha.yml"

echo "Building alpha images..."
$COMPOSE build api web

echo "Starting stateful services..."
$COMPOSE up -d postgres redis

echo "Running migrations..."
$COMPOSE run --rm api alembic upgrade head

echo "Starting application..."
$COMPOSE up -d api web nginx

echo "Waiting for readiness..."
attempt=0
until curl --fail --silent --show-error "http://127.0.0.1:${ALPHA_HTTP_PORT:-8080}/api/health/ready" >/dev/null; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 30 ]; then
    echo "Alpha readiness failed." >&2
    $COMPOSE ps
    exit 1
  fi
  sleep 2
done

APP_ENV=alpha ADMIN_API_KEY="$ADMIN_API_KEY" ALPHA_BASE_URL="http://127.0.0.1:${ALPHA_HTTP_PORT:-8080}"   "$ROOT/scripts/alpha_smoke.sh"

echo "Alpha deployment is ready behind localhost:${ALPHA_HTTP_PORT:-8080}."
echo "Terminate TLS in an external reverse proxy/load balancer and route the alpha hostname to this port."
