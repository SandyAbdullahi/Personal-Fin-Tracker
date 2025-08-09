# tests/test_transfer_api.py
from decimal import Decimal

import pytest
from django.urls import reverse
from factories import CategoryFactory, UserFactory  # if you have it

from finance.models import Transaction


@pytest.mark.django_db
def test_post_transfer_creates_two_transactions(api_client):
    u = UserFactory()
    c1 = CategoryFactory(user=u)
    c2 = CategoryFactory(user=u)
    api_client.force_authenticate(u)

    data = {
        "source_category": c1.id,
        "destination_category": c2.id,
        "amount": "125.00",
        "date": "2025-08-15",
        "description": "move",
    }
    resp = api_client.post(reverse("finance:transfers-list"), data)
    assert resp.status_code == 201, resp.data

    t_ids = resp.data.get("transactions", [])
    assert len(t_ids) == 2

    ex, inn = Transaction.objects.filter(id__in=t_ids).order_by("type")
    assert ex.type == "EX" and ex.category_id == c1.id and ex.amount == Decimal("125.00")
    assert inn.type == "IN" and inn.category_id == c2.id and inn.amount == Decimal("125.00")


@pytest.mark.django_db
def test_patch_transfer_updates_pair(api_client):
    u = UserFactory()
    c1 = CategoryFactory(user=u)
    c2 = CategoryFactory(user=u)
    c3 = CategoryFactory(user=u)
    api_client.force_authenticate(u)
    # create via API
    resp = api_client.post(
        reverse("finance:transfers-list"),
        {
            "source_category": c1.id,
            "destination_category": c2.id,
            "amount": "50.00",
            "date": "2025-08-15",
            "description": "x",
        },
    )
    tid = resp.data["id"]
    # patch amount & destination
    p = api_client.patch(
        reverse("finance:transfers-detail", args=[tid]),
        {
            "amount": "80.00",
            "destination_category": c3.id,
        },
        format="json",
    )
    assert p.status_code == 200, p.data
    t_ids = p.data["transactions"]
    ex, inn = Transaction.objects.filter(id__in=t_ids).order_by("type")
    assert ex.amount == Decimal("80.00") and inn.amount == Decimal("80.00")
    assert inn.category_id == c3.id


@pytest.mark.django_db
def test_post_transfer_validation_same_category(api_client):
    u = UserFactory()
    c = CategoryFactory(user=u)
    api_client.force_authenticate(u)
    resp = api_client.post(
        reverse("finance:transfers-list"),
        {
            "source_category": c.id,
            "destination_category": c.id,
            "amount": "10.00",
            "date": "2025-08-15",
        },
    )
    assert resp.status_code == 400
    assert "non_field_errors" in resp.data or "detail" in resp.data
