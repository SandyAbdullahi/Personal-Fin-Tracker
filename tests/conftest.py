# tests/conftest.py
"""
Global pytest fixtures & Django bootstrap for the test suite.
"""

import os
import sys
from pathlib import Path

# --------------------------------------------------------------------------- #
# 1.  Bootstrap Django with the CI settings module
# --------------------------------------------------------------------------- #
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings_ci")

# Ensure the repo root is on the import path when running `pytest` from anywhere
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import django  # noqa: E402  (import after path setup)

django.setup()

# --------------------------------------------------------------------------- #
# 2.  Shared fixtures
# --------------------------------------------------------------------------- #
import pytest  # noqa: E402
from rest_framework.test import APIClient  # noqa: E402

from tests.factories import CategoryFactory, UserFactory  # noqa: E402


@pytest.fixture
def api_client() -> APIClient:
    """Plain DRF `APIClient` (unauthenticated)."""
    return APIClient()


@pytest.fixture
def auth_user(api_client):
    """
    Creates a user *and* authenticates the provided ``api_client`` as that user.
    Returns the user instance so tests can reference it.
    """
    user = UserFactory()
    api_client.force_authenticate(user=user)
    return user


@pytest.fixture
def category(auth_user):
    """A `Category` that belongs to the authenticated user."""
    return CategoryFactory(user=auth_user)
