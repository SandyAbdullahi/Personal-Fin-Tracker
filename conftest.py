# tests/conftest.py
import os
import sys

import django
from pathlib import Path

# Point to the CI settings (or core.settings if you want)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings_ci")

# Ensure the project root is on sys.path if your tests folder is outside it
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if PROJECT_ROOT not in map(Path, sys.path):
    sys.path.insert(0, str(PROJECT_ROOT))

django.setup()

# You can add/define pytest fixtures below as usual …
