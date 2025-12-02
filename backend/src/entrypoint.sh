#!/usr/bin/env bash
set -euo pipefail
# Ensure Python outputs are unbuffered so logs appear in container stdout/stderr immediately
export PYTHONUNBUFFERED=1
# Allow overriding log level via env
export LOG_LEVEL=${LOG_LEVEL:-INFO}
# Entrypoint: robust startup for the Django app inside the container.
# Assumes project is mounted at /app or /app/src. Ensures we cd to the
# directory that contains `manage.py` and waits for the database before
# running migrations.

# locate manage.py
if [ -f "/app/manage.py" ]; then
  cd /app
elif [ -f "/app/src/manage.py" ]; then
  cd /app/src
else
  echo "manage.py not found in /app or /app/src. Listing /app for debug:" >&2
  ls -la /app || true
  echo "Exiting: manage.py required to continue" >&2
  exit 1
fi

echo "Collect static files (conditionally)"
if [ "${ENV_NAME:-dev}" != "dev" ] || [ "${FORCE_COLLECTSTATIC:-0}" = "1" ]; then
  python manage.py collectstatic --noinput || true
else
  echo "Skipping collectstatic in dev environment"
fi

echo "Resolving database host/port"
# prefer Postgres-specific env names, fall back to generic DATABASE_* names, then defaults
DB_HOST=${POSTGRES_HOST:-${DATABASE_HOST:-db}}
DB_PORT=${POSTGRES_PORT:-${DATABASE_PORT:-5432}}

echo "Waiting for DB at ${DB_HOST}:${DB_PORT}"
# Try connecting using Python/psycopg2 to ensure Postgres is fully ready (not just listening).
MAX_WAIT=120
WAITED=0
until python - <<PYCODE >/dev/null 2>&1
import os
import sys
try:
    import psycopg2
except Exception:
    sys.exit(2)
try:
    conn = psycopg2.connect(
        dbname=os.environ.get('POSTGRES_DB', os.environ.get('DATABASE_NAME', 'yura_db')),
        user=os.environ.get('POSTGRES_USER', os.environ.get('DATABASE_USER', 'yura_user')),
        password=os.environ.get('POSTGRES_PASSWORD', os.environ.get('DATABASE_PASSWORD', 'yura_password')),
        host=os.environ.get('POSTGRES_HOST', os.environ.get('DATABASE_HOST', 'db')),
        port=int(os.environ.get('POSTGRES_PORT', os.environ.get('DATABASE_PORT', '5432'))),
        connect_timeout=5,
    )
    conn.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
PYCODE
do
  if [ ${WAITED} -ge ${MAX_WAIT} ]; then
    echo "Timed out waiting for database at ${DB_HOST}:${DB_PORT}" >&2
    break
  fi
  echo "Database not ready yet, sleeping... (${WAITED}s)"
  sleep 1
  WAITED=$((WAITED+1))
done

# Only run migrations if NOT explicitly skipped
if [ "${SKIP_MIGRATIONS:-0}" != "1" ]; then
  echo "Apply database migrations"
  python manage.py makemigrations || true
  python manage.py migrate --noinput
else
  echo "Skipping database migrations (SKIP_MIGRATIONS=1)"
fi

echo "Create superuser if not exists"
# Use ADMIN_FIRST_NAME / ADMIN_LAST_NAME if provided when creating the superuser.
python manage.py shell <<PY
from api.models import User
import os
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
first = os.environ.get('ADMIN_FIRST_NAME', 'Admin')
last = os.environ.get('ADMIN_LAST_NAME', 'User')
if not User.objects.filter(email=email).exists():
  User.objects.create_superuser(email, password, first_name=first, last_name=last)
  print('Superuser created')
else:
  print('Superuser exists')
PY

# # Run all backend tests before starting the server
# if [ "${SKIP_TESTS:-0}" != "1" ]; then
#   echo "Running backend tests..."
#   python manage.py test api.tests --verbosity=2 --noinput
#   TEST_EXIT_CODE=$?
#   if [ ${TEST_EXIT_CODE} -ne 0 ]; then
#     echo "Tests failed with exit code ${TEST_EXIT_CODE}. Aborting startup." >&2
#     exit ${TEST_EXIT_CODE}
#   fi
#   echo "All tests passed successfully!"
# else
#   echo "Skipping tests (SKIP_TESTS=1)"
# fi

echo "Starting server"
if [ "${ENV_NAME:-dev}" = "dev" ]; then
  echo "Running development server"
  exec python manage.py runserver 0.0.0.0:8080
else
  echo "Running production server (gunicorn)"
  exec gunicorn -c gunicorn.conf toxbox_dep.wsgi:application
fi
