# conftest.py
"""
Global pytest configuration & fixtures.

Why we do things this way
-------------------------
* We **force** an in-memory SQLite DB during tests (`django_db_setup`)
  so CI doesn’t need a Postgres instance and collection runs faster.
* Re-usable fixtures (`user`, `category`, `api_client`) keep individual
  tests concise while still exercising real ORM behaviour.
"""

import os

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

# --------------------------------------------------------------------------- #
# 1.  Ensure the correct settings module is used
# --------------------------------------------------------------------------- #
# If `DJANGO_SETTINGS_MODULE` wasn’t already set by pytest.ini, fall back to
# the light-weight settings we created for CI (`core.settings_ci`).
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings_ci")


# --------------------------------------------------------------------------- #
# 2.  Speedy in-memory DB for all tests
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="session")
def django_db_setup():
    """
    Override DATABASES for the test session.

    Using SQLite in-memory keeps CI reliable and eliminates the need
    for additional services (e.g. Postgres) during `pytest` runs.
    """
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }


# --------------------------------------------------------------------------- #
# 3.  Common reusable fixtures
# --------------------------------------------------------------------------- #
User = get_user_model()


@pytest.fixture
def user(db):
    """A basic active user."""
    return User.objects.create_user(email="test@example.com", password="secret")


@pytest.fixture
def category(user):
    """A category owned by the `user` fixture."""
    from finance.models import Category

    return Category.objects.create(name="Groceries", user=user)


@pytest.fixture
def api_client(user):
    """
    DRF APIClient that’s already authenticated as `user`.

    Usage:
        def test_something(api_client):
            response = api_client.get("/api/…")
    """
    client = APIClient()
    client.force_authenticate(user=user)
    return client
