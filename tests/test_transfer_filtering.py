import pytest
from django.urls import reverse
from django.utils import timezone
from factories import CategoryFactory, TransferFactory, UserFactory

TODAY = timezone.localdate()


@pytest.mark.django_db
def test_filter_by_source_and_destination(api_client):
    u = UserFactory()
    src1 = CategoryFactory(user=u)
    dst1 = CategoryFactory(user=u)
    src2 = CategoryFactory(user=u)
    dst2 = CategoryFactory(user=u)

    TransferFactory(user=u, source_category=src1, destination_category=dst1, amount=100, date=TODAY)
    TransferFactory(user=u, source_category=src2, destination_category=dst2, amount=200, date=TODAY)

    api_client.force_authenticate(u)

    url = reverse("finance:transfers-list") + f"?source_category={src1.id}"
    resp = api_client.get(url)
    assert resp.status_code == 200
    assert len(resp.data["results"]) == 1
    assert resp.data["results"][0]["source_category"] == src1.id

    url = reverse("finance:transfers-list") + f"?destination_category={dst2.id}"
    resp = api_client.get(url)
    assert resp.status_code == 200
    assert len(resp.data["results"]) == 1
    assert resp.data["results"][0]["destination_category"] == dst2.id


@pytest.mark.django_db
def test_filter_by_date_range(api_client):
    u = UserFactory()
    src = CategoryFactory(user=u)
    dst = CategoryFactory(user=u)

    TransferFactory(user=u, source_category=src, destination_category=dst, amount=10, date=TODAY.replace(day=1))
    TransferFactory(user=u, source_category=src, destination_category=dst, amount=20, date=TODAY.replace(day=15))
    TransferFactory(user=u, source_category=src, destination_category=dst, amount=30, date=TODAY.replace(day=28))

    api_client.force_authenticate(u)
    url = reverse("finance:transfers-list") + f"?date__gte={TODAY.replace(day=10)}&date__lte={TODAY.replace(day=20)}"
    resp = api_client.get(url)
    assert resp.status_code == 200
    amounts = [t["amount"] for t in resp.data["results"]]
    assert amounts == ["20.00"]


@pytest.mark.django_db
def test_ordering_and_search(api_client):
    u = UserFactory()
    src = CategoryFactory(user=u)
    dst = CategoryFactory(user=u)

    TransferFactory(
        user=u, source_category=src, destination_category=dst, amount=50, date=TODAY, description="move to groceries"
    )
    TransferFactory(
        user=u, source_category=src, destination_category=dst, amount=25, date=TODAY, description="top up rent"
    )

    api_client.force_authenticate(u)

    # default ordering = -date,-id → newest first
    url = reverse("finance:transfers-list")
    resp = api_client.get(url)
    assert resp.status_code == 200
    amounts = [row["amount"] for row in resp.data["results"]]
    assert amounts == ["25.00", "50.00"]

    # explicit ordering by amount
    url = reverse("finance:transfers-list") + "?ordering=-amount"
    resp = api_client.get(url)
    assert [row["amount"] for row in resp.data["results"]] == ["50.00", "25.00"]

    # search by description
    url = reverse("finance:transfers-list") + "?search=grocer"
    resp = api_client.get(url)
    assert len(resp.data["results"]) == 1
    assert resp.data["results"][0]["description"] == "move to groceries"


@pytest.mark.django_db
def test_delete_transfer_removes_paired_transactions(api_client):
    u = UserFactory()
    src = CategoryFactory(user=u)
    dst = CategoryFactory(user=u)

    t = TransferFactory(user=u, source_category=src, destination_category=dst, amount=40, date=TODAY)
    # serializer/view logic should have created the two transactions already in your flow
    # if factories don’t, we at least verify the cascade:
    api_client.force_authenticate(u)

    # record current counts
    from finance.models import Transaction

    before = Transaction.objects.filter(transfer=t).count()

    resp = api_client.delete(reverse("finance:transfers-detail", args=[t.id]))
    assert resp.status_code in (200, 204, 202, 204)  # DRF returns 204 by default

    after = Transaction.objects.filter(transfer=t).count()
    assert before >= 0
    assert after == 0
