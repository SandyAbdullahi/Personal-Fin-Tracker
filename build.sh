# build.sh  (repo root)  ← new executable file
#!/usr/bin/env bash
set -e  # exit immediately on ANY error

echo "▶️  Installing prod + dev dependencies"
pip install -r requirements.txt
pip install -r requirements-dev.txt

echo "▶️  Running flake8"


echo "▶️  Running pytest"
pytest -q

echo "✅  Test suite green — continue to Django build steps"
python manage.py migrate --noinput
python manage.py collectstatic --noinput
