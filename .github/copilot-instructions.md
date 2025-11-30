# Guidance for AI coding agents (concise)

This file contains practical, repo-specific information to help AI coding agents be immediately productive.

**Big Picture:**
- **Monorepo split:** `backend/` (Django + DRF) and `frontend/` (Angular). The backend serves a REST API at `/api/v1` and also provides health and admin routes.
- **Dev composition:** `docker-compose.yml` wires up `db` (Postgres + pgvector), `backend` (mounted `backend/src`), and `frontend` (node dev server). See `docker-compose.yml` for ports: backend `8080`, frontend `4200`, db `5433` mapped to container `5432`.

**Auth & Security patterns (important):**
- Cookie-based JWT: backend sets `access_token` and `refresh_token` as HttpOnly cookies in `backend/src/api/views/auth.py` (SignUp/Login/Refresh/Logout).
- Backend custom authentication class: `backend/src/api/authentication.py` implements `CookieJWTAuthentication` (reads `access_token` from cookies). Many endpoints expect cookie auth + CSRF.
- Frontend expects CSRF cookie named `csrftoken` and sends it in header `X-CSRFToken` for unsafe methods. See `frontend/src/app/core/interceptor.ts` and `frontend/src/app/shared/services/auth.service.ts`.

**Environment and configuration conventions:**
- Env file for development: `dev.env`. Many env names accept either `POSTGRES_*` or `DATABASE_*` (see `backend/src/config/settings.py` and `backend/src/entrypoint.sh`).
- JWT settings and lifetimes are controlled via env vars: `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_ACCESS_TOKEN_LIFETIME_MINUTES`, `JWT_REFRESH_TOKEN_LIFETIME_DAYS`.
- `ENV_NAME=dev` disables collectstatic by default in the entrypoint; production uses Gunicorn. See `backend/src/entrypoint.sh`.

**Key files to inspect when changing behaviour:**
- `backend/src/config/settings.py` — DB, CORS, CSRF, JWT defaults, `AUTH_USER_MODEL = 'api.User'`.
- `backend/src/api/views/auth.py` — login/signup/refresh/logout cookie behavior and cookie options (httponly, secure, samesite).
- `backend/src/api/authentication.py` — cookie JWT extraction and fallback behaviour.
- `backend/src/entrypoint.sh` and `backend/Dockerfile` — container startup, DB wait logic, migrations, superuser creation.
- `docker-compose.yml` and `dev.env` — how services are wired for local development.
- `frontend/src/app/core/interceptor.ts` and `frontend/src/app/shared/environments/environment.ts` — how the frontend talks to backend and handles CSRF.

**Developer workflows & commands (copyable):**
- Start full dev stack (recommended):
```
docker-compose up --build
```
- Run backend tests inside container (or locally with same env):
```
# inside backend container
python manage.py test

# locally (if you have deps installed and DB available)
python backend/src/manage.py test
```
- Run frontend dev server locally (or via container from compose):
```
cd frontend
npm install
npm start
```
- Run backend locally (dev):
```
cd backend/src
pip install -r ../requirements.txt
python manage.py runserver 0.0.0.0:8080
```

**Project-specific conventions & gotchas:**
- The backend uses cookie-based JWTs by default and also registers `rest_framework_simplejwt.authentication.JWTAuthentication` as fallback. When adding endpoints that return tokens, prefer setting cookies like in `auth.py` instead of returning tokens in JSON.
- CSRF: frontend reads `csrftoken` cookie and adds `X-CSRFToken` for state-changing HTTP methods. New endpoints that mutate state must accept cookie credentials and respect CSRF.
- Env var name flexibility: code often checks `POSTGRES_*` then `DATABASE_*` to maximize compatibility. When adding new env-driven settings, follow this pattern.
- `AUTH_USER_MODEL` is `api.User` — modifying user fields requires inspecting `backend/src/api/models/user.py` and corresponding serializers under `backend/src/api/serializers`.

**When changing APIs / routes:**
- Update `backend/src/config/urls.py` and the files under `backend/src/api/urls/` (auth routes are in `api/urls/auth.py`). Update `frontend` calls to `environment.serverURL + '/auth/...'` where required.

**Testing guidance for AI agents:**
- Prefer using existing tests in `backend/src/api/tests/` as examples (auth tests exist). Run tests after code changes.

**If you are unsure / cannot find context:**
- Check `dev.env`, `docker-compose.yml`, and `backend/src/entrypoint.sh` for runtime behaviour. Inspect `frontend/src/app/core/interceptor.ts` to understand client-side expectations.
- Ask the maintainer for missing environment values (e.g., production secrets) before making security-impacting changes.

---
If anything above is unclear or you want more examples added (models, serializers, or a quick runbook for deploying), tell me which area to expand and I will update this file.
