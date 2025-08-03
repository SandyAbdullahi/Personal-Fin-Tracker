#!/usr/bin/env bash
set -euo pipefail

export DJANGO_SETTINGS_MODULE=core.settings_ci

echo "Running tests with settings ➜ $DJANGO_SETTINGS_MODULE"
pytest --cov=.
