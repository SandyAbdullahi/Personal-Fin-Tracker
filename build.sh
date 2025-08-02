#!/usr/bin/env bash
set -e            # exit on first error
set -x            # echo each command (helpful for logs)

# ----------------- optional: make sure psql is available -----------------
# Many Render build images already have psql; if yours doesn’t, uncomment:
# apt-get update -y
# apt-get install -y postgresql-client
# -------------------------------------------------------------------------

echo "🔍 Listing databases in the cluster to verify connectivity…"
# Connect to the always-present 'postgres' database, then \l to list them
BASE_URI=$(echo "$DATABASE_URL" | sed -E 's|/[^/]+$|/postgres|')
psql "$BASE_URI" -c '\l'


# Strip the path component so we connect to /postgres instead of /yourdb
BASE_URL=$(echo "$DATABASE_URL" | sed -E 's:/[^/]+$:/postgres:')
psql "$BASE_URL" -U "$(echo $BASE_URL | cut -d/ -f3 | cut -d: -f1)" -h "$(echo $BASE_URL | cut -d@ -f2 | cut -d/ -f1)" -c '\l'

echo "✅  Database list complete (if you see your DB above, Render can reach it)."

# …rest of your build steps…
pip install -r requirements.txt

# run tests, static checks, migrations, etc.
pytest --cov
python manage.py migrate --noinput
