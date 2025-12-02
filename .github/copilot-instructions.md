```markdown
# Guidance for AI coding agents (concise)

This file captures the project's essential architecture, conventions, and copy-pastable developer commands so an AI agent can be productive immediately.

**Big Picture**
- Monorepo split: `backend/` (Django + DRF) and `frontend/` (Angular SPA). Backend exposes API routes (prefixed under `/api/v1`) plus health/admin endpoints.
- Dev stack: `docker-compose.yml` runs `db` (Postgres + pgvector), `backend` (mounted `backend/src`), and `frontend` dev server. Ports: backend `8080`, frontend `4200`, DB host mapped to host port `5433`.

**Auth & security (project-specific)**
- Cookie-based JWTs: `access_token` and `refresh_token` are set as HttpOnly cookies in `backend/src/api/views/auth.py` (SignUp/Login/Refresh/Logout). Tokens use `rest_framework_simplejwt` with `ROTATE_REFRESH_TOKENS=True`.
- Cookie auth implementation: `backend/src/api/utils/authentication/cookie_jwt.py` implements `CookieJWTAuthentication` (extracts `access_token` from cookies and falls back to header auth).
- CSRF: SPA must fetch `csrftoken` (endpoint: `CsrfView` in `backend/src/api/views/auth.py`) — frontend reads cookie `csrftoken` and sends it as `X-CSRFToken` in unsafe requests. See `frontend/src/app/core/interceptor.ts` for exact behaviour.

**Environment & startup patterns**
- Dev env file: `dev.env`. The code often checks alternate env names (e.g., `POSTGRES_*` OR `DATABASE_*`) — follow this pattern when adding env vars.
- Important JWT env vars: `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_ACCESS_TOKEN_LIFETIME_MINUTES`, `JWT_REFRESH_TOKEN_LIFETIME_DAYS` (present in `dev.env` and referenced in `backend/src/config/settings.py`).
- Entrypoint: `backend/src/entrypoint.sh` waits for DB, runs migrations (unless `SKIP_MIGRATIONS=1`), and creates a superuser from `DJANGO_SUPERUSER_*` or `ADMIN_*` env vars. In `ENV_NAME=dev` it runs `manage.py runserver`.

**Where to look when changing behavior**
- API routing: `backend/src/config/urls.py` and `backend/src/api/urls/` (individual route files like `api/urls/auth.py`, `articles.py`).
- Auth: `backend/src/api/views/auth.py`, `backend/src/api/utils/authentication/cookie_jwt.py`, and `backend/src/api/tests/test_auth.py` (tests show cookie expectations).
- Settings: `backend/src/config/settings.py` (JWT, CORS, CSRF, `AUTH_USER_MODEL = 'api.User'`).
- Frontend integration: `frontend/src/app/core/interceptor.ts`, `frontend/src/app/shared/services/auth.service.ts`, and `frontend/src/app/shared/environments/environment.ts`.

**Developer workflows (copyable)**
- Start full dev stack (recommended):
```
docker-compose up --build
```
- Run backend tests inside container:
```
# inside backend container
python manage.py test

# locally (if you have deps and DB available)
python backend/src/manage.py test
```
- Run frontend dev server (local or via compose):
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

**Project conventions & gotchas (explicit)**
- Do not return JWTs in JSON responses for normal auth flows — set them as HttpOnly cookies (see `auth.py`). Frontend expects `withCredentials: true` (see interceptor) and uses cookie-based auth.
- Frontend retry logic: the interceptor attempts a single refresh on 401 (unless the failed request was `/auth/refresh`). Avoid creating endpoints that cause refresh loops.
- When adding environment variables, support both `POSTGRES_*` and `DATABASE_*` naming where relevant to match `entrypoint.sh` and `settings.py`.
- `AUTH_USER_MODEL` is `api.User`. Changing user fields requires updating `backend/src/api/models/user.py` and corresponding serializers (`backend/src/api/serializers`).

**When changing APIs / routes**
- Add/modify routes under `backend/src/api/urls/` and ensure they are included from `backend/src/config/urls.py`.
- Update frontend calls to `environment.serverURL + '/...` and ensure `withCredentials` and CSRF header usage are compatible (see `interceptor.ts`).

**Testing & validation**
- Use existing tests in `backend/src/api/tests/` as examples (auth tests assert cookies are set). Run tests after changes.

If any section is unclear or you want more examples (model/serializer snippets, common curl examples for cookie auth, or an integration checklist), tell me which area to expand and I'll iterate.
```
