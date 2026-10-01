#!/usr/bin/env sh
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="${ALPHA_ENV_FILE:-$ROOT/.env.alpha}"

if [ "$#" -ne 1 ]; then
  echo "Usage: ALPHA_ENV_FILE=.env.alpha ./scripts/alpha_rollback.sh <git-sha>" >&2
  exit 2
fi

TARGET_SHA="$1"

set -a
. "$ENV_FILE"
set +a

if [ "${APP_ENV:-}" != "alpha" ]; then
  echo "REFUSED: rollback only runs with APP_ENV=alpha." >&2
  exit 2
fi

echo "Rollback target: $TARGET_SHA"
echo "Use git checkout $TARGET_SHA on the alpha host, then rerun ./scripts/alpha_deploy.sh."
echo "Database downgrade is intentionally NOT automatic."
