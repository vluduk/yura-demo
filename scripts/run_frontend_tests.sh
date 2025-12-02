#!/usr/bin/env bash
set -euo pipefail

echo "[tests] Ensuring frontend container is available"
docker compose up -d --build

echo "[tests] Installing frontend deps and running tests (headless)"
# Use -T to disable pseudo-tty allocation for non-interactive
docker compose exec -T frontend sh -c "npm ci --no-audit --no-fund && npm test -- --watch=false"

EXIT_CODE=$?
echo "[tests] Frontend tests finished with exit code ${EXIT_CODE}"
exit ${EXIT_CODE}
