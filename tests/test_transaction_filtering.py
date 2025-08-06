from decimal import Decimal

import pytest
from django.urls import reverse

from tests.factories import CategoryFactory, TransactionFactory, UserFactory


@pytest.mark.django_db
def test_filter_by_type(api_client):
    u = UserFactory()
    c = CategoryFactory(user=u)
    TransactionFactory.create_batch(3, user=u, category=c, type="IN")
    TransactionFactory.create_batch(2, user=u, category=c, type="EX")

    api_client.force_authenticate(u)
    url = reverse("finance:transactions-list") + "?type=EX"
    resp = api_client.get(url)
    assert resp.status_code == 200
    assert resp.data["count"] == 2


@pytest.mark.django_db
def test_ordering(api_client):
    u = UserFactory()
    c = CategoryFactory(user=u)
    TransactionFactory(user=u, category=c, amount=10)
    TransactionFactory(user=u, category=c, amount=30)

    api_client.force_authenticate(u)
    url = reverse("finance:transactions-list") + "?ordering=-amount"
    resp = api_client.get(url)
    amounts = [Decimal(obj["amount"]) for obj in resp.data["results"]]
    assert amounts == sorted(amounts, reverse=True)
