# tests/test_transfer_serializer.py
from decimal import Decimal

import pytest
from django.utils import timezone

from finance.serializers import TransferSerializer
from tests.factories import CategoryFactory, TransactionFactory, UserFactory  # last one is only for count check

TODAY = timezone.localdate()


@pytest.mark.django_db
def test_valid_transfer_creates_two_transactions():
    """
    • serializer is valid
    • exactly two Transactions are created:
        EX from the source  (–amount)
        IN to   the dest    (+amount)
    • both belong to the same user
    """
    user = UserFactory()
    cat_src = CategoryFactory(user=user)
    cat_dst = CategoryFactory(user=user)

    data = {
        "source_category": cat_src.id,
        "destination_category": cat_dst.id,
        "amount": "250.00",
        "date": str(TODAY),
        "description": "Move to groceries envelope",
    }

    s = TransferSerializer(
        data=data,
        context={"request": type("R", (), {"user": user, "auth": True})},
    )
    assert s.is_valid(), s.errors

    before = TransactionFactory._meta.model.objects.count()
    transfer = s.save()
    after = TransactionFactory._meta.model.objects.count()

    assert after - before == 2

    tx_out, tx_in = transfer.transactions.order_by("id")
    # debit
    assert tx_out.category_id == cat_src.id
    assert tx_out.type == "EX" and tx_out.amount == Decimal("250.00")
    # credit
    assert tx_in.category_id == cat_dst.id
    assert tx_in.type == "IN" and tx_in.amount == Decimal("250.00")


@pytest.mark.django_db
@pytest.mark.parametrize("amount", ["0", "-10"])
def test_amount_must_be_positive(amount):
    user = UserFactory()
    c1 = CategoryFactory(user=user)
    c2 = CategoryFactory(user=user)

    s = TransferSerializer(
        data={
            "source_category": c1.id,
            "destination_category": c2.id,
            "amount": amount,
            "date": str(TODAY),
        },
        context={"request": type("R", (), {"user": user})},
    )
    assert not s.is_valid()
    assert "amount" in s.errors


@pytest.mark.django_db
def test_source_and_destination_cannot_match():
    user = UserFactory()
    cat = CategoryFactory(user=user)

    s = TransferSerializer(
        data={
            "source_category": cat.id,
            "destination_category": cat.id,  # same!
            "amount": "50",
            "date": str(TODAY),
        },
        context={"request": type("R", (), {"user": user})},
    )
    assert not s.is_valid()
    assert "non_field_errors" in s.errors
