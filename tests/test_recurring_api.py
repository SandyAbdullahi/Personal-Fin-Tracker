# tests/test_recurring_api.py
import datetime

import pytest
from rest_framework import status

from finance.models import RecurringTransaction, Transaction
from tests.factories import CategoryFactory, UserFactory


@pytest.mark.django_db
def test_post_due_recurring_creates_transaction(api_client):
    user = UserFactory()
    cat = CategoryFactory(user=user)
    api_client.force_authenticate(user)

    RecurringTransaction.objects.create(
        user=user,
        category=cat,
        amount="100",
        type="IN",
        description="Paycheck",
        rrule="FREQ=MONTHLY;BYMONTHDAY=1",
        next_occurrence=datetime.date.today(),
    )

    resp = api_client.post("/api/finance/post-recurring/")
    assert resp.status_code == status.HTTP_200_OK
    assert Transaction.objects.count() == 1
    assert resp.data["posted"] == 1
