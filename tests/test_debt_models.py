# tests/test_debt_models.py
from decimal import Decimal

import pytest

from finance.models import Debt, Payment
from tests.factories import UserFactory


@pytest.mark.django_db
def test_running_balance_updates():
    u = UserFactory()
    debt = Debt.objects.create(
        user=u,
        name="Car Loan",
        principal=Decimal("10000"),
        interest_rate=Decimal("7.5"),  # %
        minimum_payment=Decimal("250"),
    )
    Payment.objects.create(user=u, debt=debt, amount=Decimal("250"), date="2025-08-01")
    Payment.objects.create(user=u, debt=debt, amount=Decimal("1250"), date="2025-09-01")

    assert debt.balance == Decimal("8500")
