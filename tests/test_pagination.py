import pytest
from django.urls import reverse

from tests.factories import TransactionFactory, UserFactory


@pytest.mark.django_db
def test_transactions_are_paginated(api_client):
    user = UserFactory()
    TransactionFactory.create_batch(25, user=user)  # > one page
    api_client.force_authenticate(user)

    url = reverse("finance:transactions-list")  # /api/finance/transactions/
    resp = api_client.get(url)

    assert resp.status_code == 200
    assert len(resp.data["results"]) == 20  # default page size
    assert resp.data["next"] is not None  # link to page 2

    # page 2 contains the remaining 5
    resp2 = api_client.get(resp.data["next"])
    assert len(resp2.data["results"]) == 5
    assert resp2.data["next"] is None
