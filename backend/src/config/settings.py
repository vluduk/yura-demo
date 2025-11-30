from pathlib import Path
from datetime import timedelta
import os

import sys

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-change-me-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'drf_yasg',
    
    # Local
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        # Accept either POSTGRES_* or DATABASE_* env var names for compatibility
        'NAME': os.environ.get('POSTGRES_DB', os.environ.get('DATABASE_NAME', 'yura_db')),
        'USER': os.environ.get('POSTGRES_USER', os.environ.get('DATABASE_USER', 'yura_user')),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', os.environ.get('DATABASE_PASSWORD', 'yura_password')),
        'HOST': os.environ.get('POSTGRES_HOST', os.environ.get('DATABASE_HOST', 'localhost')),
        'PORT': os.environ.get('POSTGRES_PORT', os.environ.get('DATABASE_PORT', '5432')),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'api.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'api.authentication.CookieJWTAuthentication',  # Custom cookie-based JWT auth
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # Fallback to header-based
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}


# Helper to read secrets from a file (Docker/K8s secrets) or environment variables.
def read_secret(name: str, file_path: str | None = None) -> str | None:
    """Return secret value from a file first (if present), otherwise from environment.

    - `file_path` is an explicit path to a file containing the secret (e.g. `/run/secrets/google_api_key`).
    - If `file_path` is None, the function will check for an env var named `<name>_FILE` and
      use its value as a file path if present.
    - Falls back to `os.environ.get(name)`.
    """
    # try explicit file_path
    try:
        path = file_path or os.environ.get(f"{name}_FILE")
        if path:
            with open(path, "r") as f:
                return f.read().strip()
    except Exception:
        # ignore file read errors and fallback to env var
        pass
    return os.environ.get(name)


# Google LLM / Generative AI settings
# The view will look for `GOOGLE_API_KEY` via settings or env var. Prefer mounting this
# secret as a Docker/Swarm/Kubernetes secret at `/run/secrets/google_api_key` or setting
# an env var from your CI/CD secrets.
GOOGLE_API_KEY = read_secret('GOOGLE_API_KEY', file_path=os.environ.get('GOOGLE_API_KEY_FILE', '/run/secrets/google_api_key'))
# default model name; can be overridden in env
GOOGLE_LLM_MODEL = os.environ.get('GOOGLE_LLM_MODEL', 'gemini-1.5-flash')
# optional system prompt to include at the start of conversations
GOOGLE_LLM_SYSTEM_PROMPT = os.environ.get('GOOGLE_LLM_SYSTEM_PROMPT', '')

SIMPLE_JWT = {
    # Token Lifetimes
    'ACCESS_TOKEN_LIFETIME': timedelta(
        minutes=int(os.environ.get('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', 15))
    ),
    'REFRESH_TOKEN_LIFETIME': timedelta(
        days=int(os.environ.get('JWT_REFRESH_TOKEN_LIFETIME_DAYS', 7))
    ),
    
    # Token Blacklisting
    'ROTATE_REFRESH_TOKENS': True,  # Generate new refresh token on refresh
    'BLACKLIST_AFTER_ROTATION': True,  # Blacklist old refresh token
    'UPDATE_LAST_LOGIN': True,
    
    # Signing
    'SIGNING_KEY': os.environ.get('JWT_SECRET_KEY', SECRET_KEY),
    'ALGORITHM': os.environ.get('JWT_ALGORITHM', 'HS256'),
    
    # Auth
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    
    # Token Types
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# CORS settings for cookie-based auth
# CORS settings for cookie-based auth
CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ALLOWED_ORIGINS', 
    'http://localhost:4200,http://127.0.0.1:4200'
).split(',')
CORS_ALLOW_CREDENTIALS = True

# CSRF Protection
CSRF_COOKIE_HTTPONLY = False  # Allow frontend to read CSRF token
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = not DEBUG  # Secure in production
CSRF_TRUSTED_ORIGINS = os.environ.get(
    'CSRF_TRUSTED_ORIGINS',
    'http://localhost:4200,http://localhost:8080'
).split(',')

# Session and Cookie Security
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = 'Lax'
