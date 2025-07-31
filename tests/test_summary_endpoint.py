# tests/test_summary_endpoint.py
import json
from datetime import date

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from finance.models import Category, Transaction


def test_summary_returns_grouped_totals(db):
    # 1) Arrange
    user = get_user_model().objects.create_user(
        email="dummy@example.com", password="pass123"
    )
    cat_food = Category.objects.create(name="Food")
    cat_rent = Category.objects.create(name="Rent")

    Transaction.objects.bulk_create(
        [
            Transaction(
                user=user,
                category=cat_food,
                amount=50,
                type="EX",
                date=date(2025, 7, 2),
            ),
            Transaction(
                user=user,
                category=cat_food,
                amount=70,
                type="EX",
                date=date(2025, 7, 15),
            ),
            Transaction(
                user=user,
                category=cat_rent,
                amount=500,
                type="EX",
                date=date(2025, 7, 10),
            ),
        ]
    )

    # 2) Act
    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("finance:summary")  # or hard-code "/api/finance/summary/"
    response = client.get(url, {"start": "2025-07-01", "end": "2025-07-31"})

    # 3) Assert
    assert response.status_code == 200
    data = response.json()
    assert data["expense_total"] == 620
    assert data["income_total"] == 0
    # order in response may vary – normalise to dict for comparison
    by_cat = {row["name"]: row["total"] for row in data["by_category"]}
    assert by_cat == {"Rent": 500, "Food": 120}
