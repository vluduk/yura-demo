#!/usr/bin/env bash
set -euo pipefail

echo "[tests] Bringing up services (build if needed)"
docker compose up -d --build

echo "[tests] Running backend Django tests"
# Pass-through any args to manage.py test
ARGS="${@:-}"
if [ -z "$ARGS" ]; then
  docker compose exec -T backend python manage.py test -v 2
else
  docker compose exec -T backend python manage.py test $ARGS -v 2
fi

EXIT_CODE=$?
echo "[tests] Backend tests finished with exit code ${EXIT_CODE}"
exit ${EXIT_CODE}
