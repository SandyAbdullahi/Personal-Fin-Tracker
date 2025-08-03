# core/settings_ci.py
"""
Settings used only by pytest / Render CI.
They extend the normal project settings and then
just swap the DB for SQLite-in-memory and speed-ups.
"""
from .settings import *          # ⬅️  pull in EVERYTHING first
import os

# ------------------------------------------------------------------
# DATABASE: fast, throw-away SQLite for test run
# ------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# ------------------------------------------------------------------
# SPEED UP PASSWORD HASHING & EMAIL
# ------------------------------------------------------------------
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# ------------------------------------------------------------------
# OPTIONAL: any test-only tweaks go here
# ------------------------------------------------------------------
DEBUG = False
SECRET_KEY = os.getenv("SECRET_KEY", "ci-dummy-secret-key")
