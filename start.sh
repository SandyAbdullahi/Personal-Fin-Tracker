#!/usr/bin/env bash
set -euo pipefail
export DJANGO_SETTINGS_MODULE=core.settings_ci   # 👈

python manage.py migrate --no-input
gunicorn core.wsgi:application --log-file -
