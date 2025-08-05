#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

echo "▶️  Install production dependencies"
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

echo "▶️  Collect static assets"
# Use the same settings module you use everywhere else
export DJANGO_SETTINGS_MODULE=core.settings_ci
python manage.py collectstatic --no-input
