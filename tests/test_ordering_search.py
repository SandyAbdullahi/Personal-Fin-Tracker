import pytest
from django.urls import reverse

from tests.factories import CategoryFactory, TransactionFactory, UserFactory


@pytest.mark.django_db
def test_transaction_ordering_and_search(api_client):
    user = UserFactory()
    cat = CategoryFactory(user=user)
    # amounts 10, 20, 30
    for i in range(1, 4):
        TransactionFactory(user=user, category=cat, amount=i * 10, description=f"rent{i}")

    api_client.force_authenticate(user)

    # default ordering −date ⇒ newest first (id 3 first)
    url = reverse("finance:transactions-list")
    assert api_client.get(url).data["results"][0]["amount"] == "30.00"

    # explicit ordering
    assert api_client.get(url + "?ordering=amount").data["results"][0]["amount"] == "10.00"
    assert api_client.get(url + "?ordering=-amount").data["results"][0]["amount"] == "30.00"

    # search
    resp = api_client.get(url + "?search=rent2")
    assert resp.data["count"] == 1
    assert resp.data["results"][0]["amount"] == "20.00"
