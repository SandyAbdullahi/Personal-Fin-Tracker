# tests/test_transaction_serializer.py
import pytest

from finance.serializers import TransactionSerializer
from tests.factories import CategoryFactory, UserFactory


@pytest.mark.django_db
def test_valid_transaction():
    """
    A serializer with correct data should validate.
    """
    user = UserFactory()
    category = CategoryFactory(user=user)

    data = {
        "category_id": category.id,  # <-- key renamed
        "type": "IN",
        "amount": 200,
        "date": "2025-01-20",
        "description": "Salary",
    }

    serializer = TransactionSerializer(data=data, context={"request": None})
    assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
def test_amount_must_be_positive():
    """
    Negative amounts should raise a validation error.
    """
    user = UserFactory()
    category = CategoryFactory(user=user)

    data = {
        "category_id": category.id,  # <-- key renamed
        "type": "EX",
        "amount": -5,
        "date": "2025-01-20",
    }

    serializer = TransactionSerializer(data=data, context={"request": None})
    assert not serializer.is_valid()
    assert "amount" in serializer.errors
