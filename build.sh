#!/usr/bin/env bash
set -e

pip install -r requirements.txt
pip install -r requirements-dev.txt

# Lint only project code (option A) …
#flake8 --exclude=.venv .
flake8 --config=.flake8 .
black .
# …or, after adding .flake8 (option B):
#flake8 .

pytest -q

python manage.py migrate --noinput
python manage.py collectstatic --noinput
