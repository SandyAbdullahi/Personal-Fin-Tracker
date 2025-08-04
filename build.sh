#!/usr/bin/env bash
set -o errexit
set -o nounset

set -euo pipefail

# 1. Install everything (system libs are already in the Render image)
pip install --upgrade pip
pip install -r requirements.txt
pip install -r dev-requirements.txt

# 2. Install dev tools that are *only* needed during the build
pip install -q flake8 black pytest pytest-django pytest-cov

export DJANGO_SETTINGS_MODULE=core.settings_ci

## 3. Style / lint
flake8 .

echo "Running tests with settings ➜ $DJANGO_SETTINGS_MODULE"
python manage.py collectstatic --no-input
pytest



