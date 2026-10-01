#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")/.."

python -m pip install pip-audit
(
  cd apps/api
  pip-audit -r requirements.txt
)

(
  cd apps/web
  npm audit --audit-level=high
)

if command -v trivy >/dev/null 2>&1; then
  trivy fs --severity HIGH,CRITICAL --exit-code 1 .
  docker build -t greenbusiness-api:scan apps/api
  docker build -t greenbusiness-web:scan apps/web
  trivy image --severity HIGH,CRITICAL --exit-code 1 greenbusiness-api:scan
  trivy image --severity HIGH,CRITICAL --exit-code 1 greenbusiness-web:scan
else
  echo "Trivy not installed; dependency audits completed."
  echo "Install Trivy and rerun this script to include filesystem/container scanning."
fi
