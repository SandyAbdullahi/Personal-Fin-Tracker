#!/usr/bin/env bash
set -euo pipefail
export DJANGO_SETTINGS_MODULE=core.settings_ci   # 👈

rm finance/migrations/0*.py && rm accounts/migrations/0*.py
python manage.py makemigrations accounts finance
python manage.py migrate --no-input
gunicorn core.wsgi:application --log-file -
