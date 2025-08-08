from decimal import Decimal

import pytest
from django.urls import reverse

from tests.factories import BudgetFactory, CategoryFactory, UserFactory


@pytest.mark.django_db
def test_filter_by_category(api_client):
    user = UserFactory()
    cat_ok = CategoryFactory(user=user)
    cat_no = CategoryFactory(user=user)

    BudgetFactory(user=user, category=cat_ok, limit=100, period="M")
    BudgetFactory(user=user, category=cat_no, limit=200, period="M")

    api_client.force_authenticate(user)
    url = reverse("finance:budgets-list") + f"?category={cat_ok.id}"
    resp = api_client.get(url)

    assert resp.status_code == 200
    assert len(resp.data["results"]) == 1
    assert resp.data["results"][0]["category"] == cat_ok.id


@pytest.mark.django_db
def test_order_by_remaining(api_client):
    user = UserFactory()
    cat = CategoryFactory(user=user)

    # smaller remaining should come first when ordering=remaining
    BudgetFactory(user=user, category=cat, limit=100, period="M", spent=80)
    BudgetFactory(user=user, category=cat, limit=100, period="M", spent=10)

    api_client.force_authenticate(user)
    url = reverse("finance:budgets-list") + "?ordering=remaining"
    resp = api_client.get(url)

    remaining_values = [Decimal(b["remaining"]) for b in resp.data["results"]]
    assert remaining_values == sorted(remaining_values)
