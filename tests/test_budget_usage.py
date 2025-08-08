from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone

from tests.factories import BudgetFactory, CategoryFactory, TransactionFactory, UserFactory


@pytest.mark.django_db
def test_budget_usage_calculation(api_client):
    user = UserFactory()
    cat = CategoryFactory(user=user)

    # Budget: KES 1000 this month
    budget = BudgetFactory(user=user, category=cat, limit=Decimal("1000"), period="M")

    # Two expenses this month totalling 250
    today = timezone.localdate()
    TransactionFactory(user=user, category=cat, amount=150, type="EX", date=today)
    TransactionFactory(user=user, category=cat, amount=100, type="EX", date=today)

    api_client.force_authenticate(user)
    resp = api_client.get(reverse("finance:budgets-detail", args=[budget.pk]))

    data = resp.data
    assert data["amount_spent"] == "250.00"
    assert data["remaining"] == "750.00"
    assert data["percent_used"] == 25.0
