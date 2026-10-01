#!/usr/bin/env sh
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

: "${APP_ENV:=}"
: "${ADMIN_API_KEY:=}"
: "${ALPHA_BASE_URL:=http://localhost:8080}"

if [ "$APP_ENV" != "alpha" ]; then
  echo "REFUSED: APP_ENV must be exactly 'alpha'." >&2
  exit 2
fi

if [ -z "$ADMIN_API_KEY" ]; then
  echo "REFUSED: ADMIN_API_KEY is required." >&2
  exit 2
fi

TOKEN_RESPONSE="$(
  curl --fail --silent --show-error     -X POST     -H "X-Admin-Key: $ADMIN_API_KEY"     "$ALPHA_BASE_URL/api/v1/admin/auth/token"
)"

ADMIN_TOKEN="$(
  printf '%s' "$TOKEN_RESPONSE" | python3 -c     'import json,sys; print(json.load(sys.stdin)["access_token"])'
)"

if [ -z "$ADMIN_TOKEN" ]; then
  echo "REFUSED: admin token exchange returned no access token." >&2
  exit 2
fi

curl --fail --silent --show-error   -X POST   -H "Authorization: Bearer $ADMIN_TOKEN"   -H "Content-Type: application/json"   --data-binary "@$ROOT/apps/api/app/game_data/liveops_alpha_mini_arc.json"   "$ALPHA_BASE_URL/api/v1/admin/config/publish"   >/tmp/greenbusiness-alpha-liveops.json

echo "Published canonical Closed Alpha LiveOps preset."
echo "Active config:"
curl --fail --silent --show-error   -H "Authorization: Bearer $ADMIN_TOKEN"   "$ALPHA_BASE_URL/api/v1/admin/config/active"
echo
