# tests/test_post_recurring.py
import datetime as _dt

import pytest
from django.core.management import call_command
from freezegun import freeze_time

from finance.models import RecurringTransaction, Transaction
from tests.factories import CategoryFactory, UserFactory


@freeze_time("2025-08-01")
@pytest.mark.django_db
def test_post_recurring_creates_transaction():
    user = UserFactory()
    cat = CategoryFactory(user=user)

    rec = RecurringTransaction.objects.create(
        user=user,
        category=cat,
        amount="750",
        type="EX",
        description="Rent",
        rrule="FREQ=MONTHLY;BYMONTHDAY=1",
        next_occurrence=_dt.date(2025, 8, 1),
    )

    call_command("post_recurring")

    # one real transaction should now exist
    rec.refresh_from_db()  # NEW
    tx = Transaction.objects.get()
    assert tx.amount == rec.amount
    assert rec.next_occurrence == _dt.date(2025, 9, 1)
