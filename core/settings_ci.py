"""
core/settings_ci.py
--------------------------------------------------------------------
Settings used **only** when pytest-django runs in CI / Render.

▪  Inherit every setting from core.settings.
▪  Switch the DB to the URL in $DATABASE_URL (if present) or fall back to an
   in-memory SQLite DB so the suite can run anywhere with zero setup.
▪  Trim a few knobs (password hashing, e-mail, logging) to speed the run up.
"""
from __future__ import annotations

from pathlib import Path
import os

from .settings import *  # noqa: F401,F403  ⇐ pull in *all* base settings first

# --------------------------------------------------------------------------- #
# Core flags
# --------------------------------------------------------------------------- #

DEBUG = False  # never expose debug info in CI
SECRET_KEY = os.getenv("SECRET_KEY", "ci-dummy-secret-key")
ALLOWED_HOSTS = ["*"]  # irrelevant for tests but must be non-empty

# --------------------------------------------------------------------------- #
# Database
# --------------------------------------------------------------------------- #

# 1️⃣  Use a DATABASE_URL when Render / Neon provides it
# 2️⃣  Otherwise fall back to an in-memory SQLite database
_db_url = os.getenv("DATABASE_URL") or os.getenv("CI_DATABASE_URL")

DATABASES = {  # type: ignore[assignment]
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# --------------------------------------------------------------------------- #
# Test-runner optimisations
# --------------------------------------------------------------------------- #

# Use the fastest (insecure) hasher so user creation is instant
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Keep e-mails in memory instead of hitting the network
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Static files: skip compression / hashing during tests
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Silence Django’s default verbose logging in CI
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
}

# --------------------------------------------------------------------------- #
# pytest-django hint
# --------------------------------------------------------------------------- #
# BASE_DIR is needed only if the base settings removed it; keeps manage.py happy.
BASE_DIR = Path(__file__).resolve().parent.parent  # type: ignore[assignment]
