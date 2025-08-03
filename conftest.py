# tests/conftest.py

# conftest.py  (debug snippet – remove once it’s green)
import importlib
import os
import sys
from pathlib import Path

import django

print("DEBUG ➜ DJANGO_SETTINGS_MODULE =", os.getenv("DJANGO_SETTINGS_MODULE"))
try:
    mod = importlib.import_module(os.environ["DJANGO_SETTINGS_MODULE"])
    print(
        "DEBUG ➜ contenttypes present:",
        "django.contrib.contenttypes" in mod.INSTALLED_APPS,
    )
except Exception as exc:
    print("DEBUG ➜ could not import settings:", exc, file=sys.stderr)


# Point to the CI settings (or core.settings if you want)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings_ci")

# Ensure the project root is on sys.path if your tests folder is outside it
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if PROJECT_ROOT not in map(Path, sys.path):
    sys.path.insert(0, str(PROJECT_ROOT))

django.setup()

# You can add/define pytest fixtures below as usual …
