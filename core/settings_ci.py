"""
settings_ci.py
───────────────────────────────────────────────────────────────────────────────
Settings that are *only* loaded in CI pipelines and during Render’s build stage.

✦ Uses an in-memory SQLite DB (lightning-fast, no secrets required)
✦ Keeps INSTALLED_APPS identical to production so migrations import cleanly
✦ Ships static assets with WhiteNoise (hashed filenames + gzip/brotli)
"""

import os
from pathlib import Path

import dj_database_url

# ─────────────────────────── core ────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "ci-secret-key"
DEBUG = True

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "personal-fin-tracker.onrender.com",
]


CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # If you use Next.js or another port in dev:
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # plus any prod origins…
]
# Render preview/production URLs
if host := os.getenv("RENDER_EXTERNAL_HOSTNAME"):
    ALLOWED_HOSTS.append(host)

# ───────────────────────── apps & middleware ────────────────────────────────
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3ʳᵈ-party
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "drf_spectacular",
    # Local
    "accounts",
    "finance",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # ← must follow Security
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"

# ─────────────────────────── database ───────────────────────────────────────
#
# • In CI we don’t want a Postgres container, so default to SQLite-in-memory.
# • If DATABASE_URL *is* defined (e.g. on Render preview builds), use that.
#
DATABASE_URL = os.getenv("DATABASE_URL")

DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL or "sqlite://:memory:",
        conn_max_age=600,
    )
}

# ───────────────────────── static files / WhiteNoise ────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    }
}

WHITENOISE_AUTOREFRESH = DEBUG  # auto-reload locally
WHITENOISE_MAX_AGE = 60 * 60 * 24 * 30  # 30 days

# ─────────────────────────── templates ──────────────────────────────────────
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
    }
]

# ─────────────────────────── DRF defaults ───────────────────────────────────
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
    "DESCRIPTION": ("Public endpoints for categories, transactions, savings goals " "and recurring transactions."),
    "COMPONENT_SPLIT_REQUEST": True,
    "SERVERS": [{"url": "/"}],
    "TAGS": [{"name": "Transfers", "description": "Move funds between categories"}],
}

# ─────────────────────────── misc / i18n ────────────────────────────────────
AUTH_USER_MODEL = "accounts.CustomUser"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Nairobi"  # ← Kenya
USE_I18N = True
USE_TZ = True
