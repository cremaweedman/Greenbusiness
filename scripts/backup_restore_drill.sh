#!/usr/bin/env sh
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_DIR="$ROOT/backups"
mkdir -p "$BACKUP_DIR"

STAMP="$(date +%Y%m%d-%H%M%S)"
DUMP="$BACKUP_DIR/greenbusiness-$STAMP.dump"

docker compose -f "$ROOT/docker-compose.yml" exec -T postgres pg_dump \
  -U "${POSTGRES_USER:-greenbusiness}" \
  -d "${POSTGRES_DB:-greenbusiness}" \
  --format=custom > "$DUMP"

test -s "$DUMP"
echo "Backup written: $DUMP"
echo "Restore into an isolated database according to docs/BACKUP_RESTORE_RUNBOOK.md"
