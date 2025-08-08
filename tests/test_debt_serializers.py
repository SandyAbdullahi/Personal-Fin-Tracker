# tests/test_debt_serializers.py
from decimal import Decimal

import pytest

from finance.serializers import PaymentSerializer
from tests.factories import DebtFactory, UserFactory


@pytest.mark.django_db
def test_payment_serializer_validates_and_updates_balance():
    u = UserFactory()
    debt = DebtFactory(user=u, principal=Decimal("5000"))
    data = {"debt": debt.id, "amount": "500", "date": "2025-08-15"}
    s = PaymentSerializer(data=data, context={"request": type("R", (), {"user": u})})
    assert s.is_valid(), s.errors
    _ = s.save()
    debt.refresh_from_db()
    assert debt.balance == Decimal("4500")
