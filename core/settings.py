import os
from pathlib import Path

import dj_database_url
import django_heroku
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = config("DATABASE_URL", default=None)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", cast=bool)

ALLOWED_HOSTS = [
    ".onrender.com",
    "localhost",
    "127.0.0.1",
    "personal-fin-tracker.onrender.com",
]


# Static files
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
# WhiteNoise settings
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_AUTOREFRESH = DEBUG  # auto-reload locally
WHITENOISE_MAX_AGE = 60 * 60 * 24 * 30  # 30 days

# Application definition
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "drf_spectacular",
    # Custom apps
    "accounts",
    "finance",
]

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
    "DESCRIPTION": "Public endpoints for categories, transactions, savings " "goals and recurring transactions.",
    # generate shorter component names
    "COMPONENT_SPLIT_REQUEST": True,
}


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

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

# Database

# Use Render’s INTERNAL_DATABASE_URL if it exists.
# Otherwise fall back to DATABASE_URL (works with Neon, Supabase, etc.),
# and if *that*’s missing fall back to a local sqlite file.
DATABASES = {
    "default": dj_database_url.parse(
        os.getenv("INTERNAL_DATABASE_URL")
        or os.getenv("DATABASE_URL")  # e.g. your Neon string
        or f"sqlite:///{BASE_DIR / 'db.sqlite3'}",  # dev fallback
        conn_max_age=600,
        ssl_require=bool(os.getenv("INTERNAL_DATABASE_URL")),
    )
}

# Give Django something harmless for its test DB when this settings file *is*
# used in tests (it usually isn’t – we have settings_ci.py for that).
DATABASES["default"]["TEST"] = {"NAME": "test_db"}

# Activate Render's static file and DB configs
django_heroku.settings(locals())

# Optional (production safety)
CSRF_TRUSTED_ORIGINS = ["https://*.onrender.com"]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


AUTH_USER_MODEL = "accounts.CustomUser"


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Nairobi"  # Nairobi, Kenya

USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
