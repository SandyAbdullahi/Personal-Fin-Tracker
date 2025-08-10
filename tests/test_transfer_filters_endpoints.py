# tests/test_transfer_filters_endpoints.py
from datetime import date, timedelta

import pytest
from django.urls import reverse
from factories import CategoryFactory, TransferFactory, UserFactory

from finance.models import Transaction

TODAY = date.today()


@pytest.mark.django_db
def test_list_filters_by_source_and_date_and_orders(api_client):
    u = UserFactory()
    c1 = CategoryFactory(user=u)
    c2 = CategoryFactory(user=u)

    # three transfers for the same user
    t1 = TransferFactory(
        user=u,
        source_category=c1,
        destination_category=c2,
        amount="100.00",
        date=TODAY - timedelta(days=2),
        description="first",
    )
    t2 = TransferFactory(
        user=u,
        source_category=c1,
        destination_category=c2,
        amount="300.00",
        date=TODAY - timedelta(days=1),
        description="second",
    )
    t3 = TransferFactory(
        user=u, source_category=c2, destination_category=c1, amount="200.00", date=TODAY, description="third"
    )

    # someone else's transfer (should be invisible)
    _ = TransferFactory()  # different user via factory

    api_client.force_authenticate(u)

    base = reverse("finance:transfers-list")

    # filter by source_category=c1 (should return t1,t2 only)
    resp = api_client.get(base, {"source_category": c1.id})
    ids = [row["id"] for row in resp.data["results"]]
    assert set(ids) == {t1.id, t2.id}

    # date range: from yesterday to today -> t2,t3
    resp = api_client.get(base, {"date__gte": (TODAY - timedelta(days=1)).isoformat(), "date__lte": TODAY.isoformat()})
    ids = [row["id"] for row in resp.data["results"]]
    assert set(ids) == {t2.id, t3.id}

    # ordering by amount ascending -> smallest first
    resp = api_client.get(base, {"ordering": "amount"})
    amounts = [row["amount"] for row in resp.data["results"]]
    assert amounts == sorted(amounts)

    # search by description
    resp = api_client.get(base, {"search": "second"})
    ids = [row["id"] for row in resp.data["results"]]
    assert ids == [t2.id]


@pytest.mark.django_db
def test_delete_transfer_cascades_pair(api_client):
    u = UserFactory()
    c1 = CategoryFactory(user=u)
    c2 = CategoryFactory(user=u)
    tr = TransferFactory(user=u, source_category=c1, destination_category=c2, amount="50.00", date=TODAY)

    # safety: two mirrored transactions exist
    assert Transaction.objects.filter(transfer=tr).count() == 2

    api_client.force_authenticate(u)
    url = reverse("finance:transfers-detail", args=[tr.id])
    resp = api_client.delete(url)
    assert resp.status_code in (200, 204)

    # both linked transactions should be gone
    assert Transaction.objects.filter(transfer=tr).count() == 0
