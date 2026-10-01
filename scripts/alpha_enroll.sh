#!/usr/bin/env sh
set -eu

: "${APP_ENV:=}"
: "${ADMIN_API_KEY:=}"
: "${ALPHA_BASE_URL:=http://localhost:8080}"
: "${ALPHA_USER_ID:=}"
: "${ALPHA_WAVE:=wave-1}"

if [ "$APP_ENV" != "alpha" ]; then
  echo "REFUSED: APP_ENV must be exactly 'alpha'." >&2
  exit 2
fi

if [ -z "$ADMIN_API_KEY" ] || [ -z "$ALPHA_USER_ID" ]; then
  echo "Usage: APP_ENV=alpha ADMIN_API_KEY=... ALPHA_USER_ID=<uuid> [ALPHA_WAVE=wave-1] scripts/alpha_enroll.sh" >&2
  exit 2
fi

TOKEN_RESPONSE="$(
  curl --fail --silent --show-error     -X POST     -H "X-Admin-Key: $ADMIN_API_KEY"     "$ALPHA_BASE_URL/api/v1/admin/auth/token"
)"

ADMIN_TOKEN="$(
  printf '%s' "$TOKEN_RESPONSE" | python3 -c     'import json,sys; print(json.load(sys.stdin)["access_token"])'
)"

curl --fail --silent --show-error   -X POST   -H "Authorization: Bearer $ADMIN_TOKEN"   -H "Content-Type: application/json"   --data "{"wave":"$ALPHA_WAVE"}"   "$ALPHA_BASE_URL/api/v1/admin/alpha/cohort/$ALPHA_USER_ID"
echo
