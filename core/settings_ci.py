# core/settings_ci.py
"""
Minimal settings overrides used only by pytest in CI.
Anything we *don’t* touch falls back to the regular settings.
"""
from .settings import *          # noqa: F403  (import everything)

# ── Fast, throw-away, in-memory SQLite DB ────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",      # pytest-django will create & migrate in RAM
    }
}

# Optional speed-ups / noise reducers ---------------------------
DEBUG = False                    # keep tests quiet
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
