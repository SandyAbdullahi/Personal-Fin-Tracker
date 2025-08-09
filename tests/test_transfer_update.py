import pytest
from django.utils import timezone

from finance.serializers import TransferSerializer
from tests.factories import CategoryFactory, UserFactory  # adjust import path if needed

TODAY = timezone.localdate()


def _req(user):
    # minimal request-like object for serializer context
    return type("R", (), {"user": user, "auth": True})


@pytest.mark.django_db
def test_transfer_update_syncs_amount_date_and_description():
    user = UserFactory()
    src = CategoryFactory(user=user)
    dst = CategoryFactory(user=user)

    # create via serializer so mirrored TXs exist
    create_data = {
        "source_category": src.id,
        "destination_category": dst.id,
        "amount": "100.00",
        "date": str(TODAY),
        "description": "initial",
    }
    s = TransferSerializer(data=create_data, context={"request": _req(user)})
    assert s.is_valid(), s.errors
    transfer = s.save()

    # update amount/date/description
    new_date = TODAY.replace(day=min(28, TODAY.day))  # safe day-in-month
    upd = TransferSerializer(
        instance=transfer,
        data={"amount": "250.00", "date": str(new_date), "description": "updated"},
        partial=True,
        context={"request": _req(user)},
    )
    assert upd.is_valid(), upd.errors
    upd.save()

    # still exactly two mirrored transactions, both linked
    txs = list(transfer.transactions.order_by("id"))
    assert len(txs) == 2
    amounts = {str(t.amount) for t in txs}
    assert amounts == {"250.00"}
    dates = {t.date for t in txs}
    assert dates == {new_date}
    # types and categories preserved
    kinds = {t.type for t in txs}
    assert kinds == {"EX", "IN"}
    by_type = {t.type: t for t in txs}
    assert by_type["EX"].category_id == src.id
    assert by_type["IN"].category_id == dst.id
    assert {t.description for t in txs} == {"updated"}


@pytest.mark.django_db
def test_transfer_update_changes_categories_correctly():
    user = UserFactory()
    src = CategoryFactory(user=user)
    dst = CategoryFactory(user=user)
    new_src = CategoryFactory(user=user)
    new_dst = CategoryFactory(user=user)

    s = TransferSerializer(
        data={
            "source_category": src.id,
            "destination_category": dst.id,
            "amount": "75.00",
            "date": str(TODAY),
        },
        context={"request": _req(user)},
    )
    assert s.is_valid(), s.errors
    transfer = s.save()

    upd = TransferSerializer(
        instance=transfer,
        data={"source_category": new_src.id, "destination_category": new_dst.id},
        partial=True,
        context={"request": _req(user)},
    )
    assert upd.is_valid(), upd.errors
    upd.save()

    txs = list(transfer.transactions.order_by("id"))
    assert len(txs) == 2
    by_type = {t.type: t for t in txs}
    assert by_type["EX"].category_id == new_src.id
    assert by_type["IN"].category_id == new_dst.id


@pytest.mark.django_db
def test_transfer_update_heals_missing_pair():
    """
    If one of the mirrored rows is missing, update() should recreate the pair.
    """
    user = UserFactory()
    src = CategoryFactory(user=user)
    dst = CategoryFactory(user=user)

    s = TransferSerializer(
        data={
            "source_category": src.id,
            "destination_category": dst.id,
            "amount": "10.00",
            "date": str(TODAY),
            "description": "heal-me",
        },
        context={"request": _req(user)},
    )
    assert s.is_valid(), s.errors
    transfer = s.save()

    # simulate corruption: remove one
    victim = transfer.transactions.first()
    victim.delete()

    # run an update with no changes (partial) to trigger healing
    upd = TransferSerializer(
        instance=transfer,
        data={"description": "heal-me"},  # no actual change needed
        partial=True,
        context={"request": _req(user)},
    )
    assert upd.is_valid(), upd.errors
    upd.save()

    txs = list(transfer.transactions.order_by("id"))
    assert len(txs) == 2
    kinds = sorted(t.type for t in txs)
    assert kinds == ["EX", "IN"]
    by_type = {t.type: t for t in txs}
    assert by_type["EX"].category_id == src.id
    assert by_type["IN"].category_id == dst.id
    assert {str(t.amount) for t in txs} == {"10.00"}
