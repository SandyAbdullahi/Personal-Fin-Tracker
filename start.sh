#!/usr/bin/env bash
set -euo pipefail          # exit on any error

# ─── 1. Environment ──────────────────────────────────────────────────────────
export DJANGO_SETTINGS_MODULE=core.settings_ci      # same one you used in build
export PYTHONUNBUFFERED=1                           # log straight to stdout

# ─── 2. Database migrations ─────────────────────────────────────────────────
rm finance/migrations/0*.py && rm accounts/migrations/0*.py
python manage.py makemigrations finance accounts
python manage.py migrate --no-input

# ─── 3. Collect static files  (only if you actually serve them) ─────────────
#python manage.py collectstatic --no-input

# ─── 4. Launch the app with Gunicorn ────────────────────────────────────────
#  -w: workers = $(CPU cores * 2) + 1   ─ adjust if you like
#  --max-requests 500  --max-requests-jitter 50   ⇒ avoid memory leaks
gunicorn core.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 3 \
    --max-requests 500 --max-requests-jitter 50 \
    --access-logfile - --error-logfile -
