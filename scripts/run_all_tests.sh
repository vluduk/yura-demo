#!/usr/bin/env bash
set -euo pipefail

echo "[tests] Running backend tests"
bash ./scripts/run_backend_tests.sh "$@"
BACK_EXIT=$?
if [ $BACK_EXIT -ne 0 ]; then
  echo "[tests] Backend tests failed (exit ${BACK_EXIT}). Aborting."
  exit $BACK_EXIT
fi

# By default we skip frontend tests because Angular test runner often requires
# a headless browser environment. Pass `--with-frontend` to run frontend tests.
RUN_FRONTEND=0
for a in "$@"; do
  if [ "$a" = "--with-frontend" ] || [ "$a" = "--frontend" ]; then
    RUN_FRONTEND=1
  fi
done

if [ $RUN_FRONTEND -eq 1 ]; then
  echo "[tests] Running frontend tests (requested)"
  bash ./scripts/run_frontend_tests.sh
  FR_EXIT=$?
  if [ $FR_EXIT -ne 0 ]; then
    echo "[tests] Frontend tests failed (exit ${FR_EXIT})."
    exit $FR_EXIT
  fi
else
  echo "[tests] Skipping frontend tests (pass --with-frontend to run them)"
fi

echo "[tests] All requested tests passed"
exit 0
