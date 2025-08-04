# ── tests/test_summary_endpoint.py ─────────────────────────────────────────────
"""
Integration-style test for the /api/finance/summary/ endpoint.

We deliberately configure Django *before* importing any project code so that
pytest-django never has a chance to pick up the wrong settings module.
"""
import os

# 1) Point Django at the lightweight test settings.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings_ci")

# 2) Now initialise Django *before* we import project models, views, etc.
import django  # noqa: E402  (flake8: ignore "import not at top of file")
django.setup()

# ──────────────────────────────────────────────────────────────────────────────
# import json
from datetime import date

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import CustomUser
from finance.models import Category, Transaction

pytestmark = pytest.mark.django_db


def test_summary_returns_grouped_totals():
    """
    POST some transactions, hit /api/finance/summary/, and check the grouping
    logic (income total, expense total, per-category breakdown).
    """
    user = CustomUser.objects.create_user(
        email="test@example.com", password="secret123"
    )

    food = Category.objects.create(name="Food", user=user)
    salary = Category.objects.create(name="Salary", user=user)

    Transaction.objects.bulk_create(
        [
            Transaction(
                user=user,
                category=salary,
                type="IN",
                amount=3_000,
                date=date(2025, 7, 10),
                description="Pay cheque",
            ),
            Transaction(
                user=user,
                category=food,
                type="EX",
                amount=50,
                date=date(2025, 7, 12),
                description="Groceries",
            ),
            Transaction(
                user=user,
                category=food,
                type="EX",
                amount=30,
                date=date(2025, 7, 14),
                description="Take-away",
            ),
        ]
    )

    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse("finance:summary")  # adjust if you used a different name
    resp = client.get(
        url,
        {"start": "2025-07-01", "end": "2025-07-31"},
        format="json",
    )

    assert resp.status_code == 200

    data = resp.json()
    assert data["income_total"] == 3000
    assert data["expense_total"] == 80

    # Categories come back ordered by -total, so Salary first.
    assert data["by_category"][0] == {"name": "Salary", "total": 3000}
    assert data["by_category"][1] == {"name": "Food", "total": 80}
