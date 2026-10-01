#!/usr/bin/env sh
set -eu

: "${APP_ENV:=}"
: "${ADMIN_API_KEY:=}"
: "${ALPHA_BASE_URL:=http://localhost:8080}"

if [ "$APP_ENV" != "alpha" ]; then
  echo "REFUSED: APP_ENV must be exactly 'alpha'." >&2
  exit 2
fi

curl --fail --silent --show-error "$ALPHA_BASE_URL/api/health/live" >/dev/null
curl --fail --silent --show-error "$ALPHA_BASE_URL/api/health/ready" >/dev/null

TOKEN_RESPONSE="$(
  curl --fail --silent --show-error     -X POST     -H "X-Admin-Key: $ADMIN_API_KEY"     "$ALPHA_BASE_URL/api/v1/admin/auth/token"
)"
ADMIN_TOKEN="$(
  printf '%s' "$TOKEN_RESPONSE" | python3 -c     'import json,sys; print(json.load(sys.stdin)["access_token"])'
)"

curl --fail --silent --show-error   -H "Authorization: Bearer $ADMIN_TOKEN"   "$ALPHA_BASE_URL/api/v1/admin/alpha/dashboard"

echo
echo "Alpha readiness smoke passed."
