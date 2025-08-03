# conftest.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings_ci")
django.setup()      # Run the full Django initialisation before tests are imported
