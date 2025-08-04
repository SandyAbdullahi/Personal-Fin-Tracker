"""
Settings used **only** during CI / Render-builds.

▪️  Always uses in-memory SQLite → no env var needed.
▪️  Keeps INSTALLED_APPS identical to production so migrations load.
"""
from pathlib import Path
# from .settings import *

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "ci-secret-key"
DEBUG = True
ALLOWED_HOSTS: list[str] = []

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3rd-party
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    # Local apps
    "accounts",
    "finance",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"

# ── THE IMPORTANT BIT ────────────────────────────────────────────────────────
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
# ─────────────────────────────────────────────────────────────────────────────

AUTH_USER_MODEL = "accounts.CustomUser"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ─── static files ──────────────────────────────────────────────────────────
# Django only needs STATIC_ROOT to be *something* pointing to the filesystem
# while it builds.  It won't actually be served during test runs.
STATIC_ROOT = Path(BASE_DIR) / "staticfiles_ci"
STATIC_URL = "/static/"            # keep the default

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}

# ─── templates (re-add DjangoTemplates so admin works) ──────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],                       # keep or trim as you like
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                # only the processors admin needs
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
            ],
        },
    }
]