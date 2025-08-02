#!/usr/bin/env bash
set -e
set -x            # echo each command (helpful for logs)

# ----------------- optional: make sure psql is available -----------------
# Many Render build images already have psql; if yours doesn’t, uncomment:
# apt-get update -y
# apt-get install -y postgresql-client
# -------------------------------------------------------------------------

echo "🔍 Listing databases in the cluster to verify connectivity…"
# Connect to the always-present 'postgres' database, then \l to list them
PGPASSWORD=$(python - <<'PY'
import os, re, sys, urllib.parse as up
url = up.urlparse(os.environ['DATABASE_URL'])
print(up.unquote(url.password or ''))
PY)

# Strip the path component so we connect to /postgres instead of /yourdb
BASE_URL=$(echo "$DATABASE_URL" | sed -E 's:/[^/]+$:/postgres:')
psql "$BASE_URL" -U "$(echo $BASE_URL | cut -d/ -f3 | cut -d: -f1)" -h "$(echo $BASE_URL | cut -d@ -f2 | cut -d/ -f1)" -c '\l'

echo "✅  Database list complete (if you see your DB above, Render can reach it)."

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
