from decimal import Decimal

import pytest

from finance.serializers import BudgetSerializer  # will exist soon
from tests.factories import CategoryFactory, UserFactory


@pytest.mark.django_db
def test_valid_budget():
    """
    Happy-path: user sets a $400 monthly limit for Groceries.
    """
    user = UserFactory()
    cat = CategoryFactory(user=user)

    data = {
        "category": cat.id,  # FK as plain int
        "limit": "400.00",
        "period": "M",  # Monthly
    }

    serializer = BudgetSerializer(data=data, context={"request_user": user})
    assert serializer.is_valid(), serializer.errors
    budget = serializer.save()
    assert budget.limit == Decimal("400.00")
    assert budget.user == user
    assert budget.period == "M"


@pytest.mark.django_db
def test_limit_must_be_positive():
    """
    Validation: limit must be > 0.
    """
    user = UserFactory()
    cat = CategoryFactory(user=user)

    bad_data = {"category": cat.id, "limit": "-50", "period": "M"}
    serializer = BudgetSerializer(data=bad_data, context={"request_user": user})
    assert not serializer.is_valid()
    assert "limit" in serializer.errors
