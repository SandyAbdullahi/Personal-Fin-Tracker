#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

# 1. Install everything (system libs are already in the Render image)
pip install --upgrade -r requirements.txt

# 2. Install dev tools that are *only* needed during the build
pip install -q flake8 black pytest pytest-django pytest-cov

# 3. Style / lint
flake8 .

# 4. Unit tests — pytest automatically picks core.settings_ci via pytest.ini
pytest

# 5. Collect static files & run migrations **with your normal settings**
python manage.py collectstatic --noinput
python manage.py migrate --noinput
