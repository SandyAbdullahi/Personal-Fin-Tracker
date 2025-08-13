"""
core/settings.py  ―  main runtime settings (Render & local)

Environment variables expected:
  • SECRET_KEY
  • DEBUG                  → “True” or “False”
  • DATABASE_URL           → optional; Neon / Supabase / PG connection string
  • INTERNAL_DATABASE_URL  → Render’s internal Postgres URL (when present)

You may keep settings_ci.py for pytest; this file is for normal runs.
"""

import os
from pathlib import Path

import dj_database_url
import django_heroku  # staticfiles helpers; we'll prevent it from overriding DBs
from decouple import config
from dotenv import load_dotenv

# ────────────────────────────────────────────────────────────────────────────────
#  BASE & SECURITY
# ────────────────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", cast=bool, default=False)

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".onrender.com",
    "personal-fin-tracker.onrender.com",
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True  # only needed if you use cookies; harmless otherwise

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://*.onrender.com",
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# These only matter when DEBUG = False
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30 if not DEBUG else 0  # 30 days
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True

# ────────────────────────────────────────────────────────────────────────────────
#  APPS
# ────────────────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    # 3rd-party
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "drf_spectacular",
    # Local
    "accounts",
    "finance",
]

AUTH_USER_MODEL = "accounts.CustomUser"

# ────────────────────────────────────────────────────────────────────────────────
#  MIDDLEWARE  (WhiteNoise *immediately* after SecurityMiddleware)
# ────────────────────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ────────────────────────────────────────────────────────────────────────────────
#  TEMPLATES / WSGI
# ────────────────────────────────────────────────────────────────────────────────
ROOT_URLCONF = "core.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
WSGI_APPLICATION = "core.wsgi.application"

# ────────────────────────────────────────────────────────────────────────────────
#  DATABASE  (Render → Neon → local Postgres fallback)
# ────────────────────────────────────────────────────────────────────────────────
# Note: We never force SSL at parse(). We set sslmode explicitly below.
RAW_DB_URL = (
    os.getenv("INTERNAL_DATABASE_URL")
    or os.getenv("DATABASE_URL")
    or "postgres://postgres:postgres@localhost:5432/fintracker"
)

db_cfg = dj_database_url.parse(
    RAW_DB_URL,
    conn_max_age=600,
    ssl_require=False,  # don't force; we'll manage it via OPTIONS.sslmode
)

# If using Postgres, control sslmode per environment
if db_cfg.get("ENGINE", "").endswith("postgresql"):
    db_cfg.setdefault("OPTIONS", {})
    if DEBUG:
        # Local dev: turn SSL off to avoid “server does not support SSL” errors
        db_cfg["OPTIONS"]["sslmode"] = "disable"
    else:
        # Production (Render internal PG): require SSL only when INTERNAL_DATABASE_URL is set
        if os.getenv("INTERNAL_DATABASE_URL"):
            db_cfg["OPTIONS"]["sslmode"] = "require"

DATABASES = {"default": db_cfg}
DATABASES["default"]["TEST"] = {"NAME": "test_db"}

# ────────────────────────────────────────────────────────────────────────────────
#  STATIC & WhiteNoise
# ────────────────────────────────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # collectstatic target
STATICFILES_DIRS = [BASE_DIR / "static"]  # for local dev assets

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_AUTOREFRESH = DEBUG  # auto-reload locally
WHITENOISE_MAX_AGE = 60 * 60 * 24 * 30  # 30 days

# ────────────────────────────────────────────────────────────────────────────────
#  Django-Rest-Framework & Spectacular
# ────────────────────────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "finance.pagination.StandardResultsSetPagination",
    "PAGE_SIZE": 20,
    "ORDERING_PARAM": "ordering",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Personal Finance Tracker API",
    "VERSION": "0.1.0",
    "DESCRIPTION": ("Public endpoints for categories, transactions, savings goals and recurring transactions."),
    "COMPONENT_SPLIT_REQUEST": True,
    "SERVERS": [{"url": "/"}],
    "TAGS": [{"name": "Transfers", "description": "Move funds between categories"}],
}

# ────────────────────────────────────────────────────────────────────────────────
#  I18N / TZ  (Kenya)
# ────────────────────────────────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Nairobi"
USE_I18N = True
USE_TZ = True

# ────────────────────────────────────────────────────────────────────────────────
#  PASSWORD VALIDATORS
# ────────────────────────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ────────────────────────────────────────────────────────────────────────────────
#  DEFAULTS
# ────────────────────────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ────────────────────────────────────────────────────────────────────────────────
#  Activate Heroku helper (static, etc.) but DO NOT let it override DATABASES
# ────────────────────────────────────────────────────────────────────────────────
if os.getenv("DYNO") or os.getenv("RENDER"):
    django_heroku.settings(locals(), databases=False)  # don't touch DATABASES
