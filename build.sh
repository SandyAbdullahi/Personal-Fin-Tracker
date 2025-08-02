#!/usr/bin/env bash
set -e
set -x

echo "🔍 Listing databases in the cluster to verify connectivity…"
psql -c '\l'
#psql "$DATABASE_URL" -c '\dt'

pip install -r requirements.txt
pip install -r requirements-dev.txt

# Lint only project code (option A) …
# flake8 --exclude=.venv .

# …or, after adding .flake8 (option B):
flake8 .

echo "▶️  Running unit/integration tests"
pytest --cov=finance --cov=accounts --cov-report=term-missing -q


#python manage.py migrate --noinput
#python manage.py collectstatic --noinput
