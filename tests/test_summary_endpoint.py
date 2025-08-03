# tests/test_summary_endpoint.py
import json

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from finance.models import Category, Transaction


@pytest.mark.django_db
def test_summary_returns_grouped_totals():
    """
    Hitting /api/finance/summary/ with a date range should return
    grouped income/expense totals and category breakdown.
    """
    user = Category.objects.create(name="Salary").user  # quick user from FK
    client = APIClient()
    client.force_authenticate(user=user)

    # Create some sample data
    salary_cat = Category.objects.get(name="Salary")
    food_cat = Category.objects.create(name="Food", user=user)

    Transaction.objects.bulk_create(
        [
            Transaction(
                user=user,
                category=salary_cat,
                type="IN",
                amount=5_000,
                date="2025-07-10",
                description="Pay cheque",
            ),
            Transaction(
                user=user,
                category=food_cat,
                type="EX",
                amount=200,
                date="2025-07-11",
                description="Groceries",
            ),
            Transaction(
                user=user,
                category=food_cat,
                type="EX",
                amount=50,
                date="2025-07-12",
                description="Take-away",
            ),
        ]
    )

    url = reverse("finance-summary")  # mapped in finance/urls.py
    resp = client.get(
        url,
        {"start": "2025-07-01", "end": "2025-07-31"},
        format="json",
    )

    assert resp.status_code == 200

    data = resp.json()
    assert data["income_total"] == 5000
    assert data["expense_total"] == 250

    # Category breakdown should be sorted by -total in the view
    assert data["by_category"][0]["name"] == "Food"
    assert data["by_category"][0]["total"] == 250
    assert data["by_category"][1]["name"] == "Salary"
    assert data["by_category"][1]["total"] == 5000
