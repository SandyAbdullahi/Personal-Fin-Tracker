# tests/test_transaction_endpoint.py
import pytest
from django.urls import reverse
from rest_framework import status
from tests.factories import TransactionFactory


@pytest.mark.django_db
def test_create_transaction(api_client, auth_user, category):
    url = reverse("finance:transactions-list")  # ← here
    payload = {
        "category": category.id,
        "type": "EX",
        "amount": 75,
        "date": "2025-01-02",
        "description": "Groceries",
    }
    api_client.force_authenticate(auth_user)
    resp = api_client.post(url, payload, format="json")
    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.data["amount"] == "75.00"


@pytest.mark.django_db
def test_summary_regression(api_client, auth_user):
    TransactionFactory.create_batch(3, user=auth_user)
    api_client.force_authenticate(auth_user)
    resp = api_client.get("/api/finance/summary/")
    assert resp.status_code == 200
    assert "by_category" in resp.data
