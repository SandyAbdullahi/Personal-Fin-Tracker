#!/usr/bin/env bash
set -euo pipefail         # fail hard on any error

echo "▶️  Using Python $(python --version)"

##############################################################################
# 1. Install production + dev dependencies
##############################################################################
pip install --upgrade pip wheel
pip install -r requirements.txt

# Only install these in CI / build -- they are *not* needed at runtime
pip install \
  black==25.1.0 \
  flake8==7.3.0 \
  flake8-bugbear==24.12.12 \
  pytest==8.4.1 \
  pytest-cov==6.2.1 \
  pytest-django==4.11.1 \
  coverage==7.10.1

##############################################################################
# 2. Static code quality - Black (format) + Flake8 (lint)
##############################################################################
echo "▶️  Formatting code with Black (check-only)…"
black . --check

echo "▶️  Linting with Flake8…"
flake8 .

##############################################################################
# 3. Run unit / integration tests with coverage
##############################################################################
echo "▶️  Running pytest suite…"
pytest --cov=finance --cov=accounts --cov-report=term-missing -q

##############################################################################
# 4. Django collectstatic (if you’re serving static files from Render)
##############################################################################
echo "▶️  Collecting static files…"
python manage.py collectstatic --noinput

echo "✅  build.sh finished successfully"
