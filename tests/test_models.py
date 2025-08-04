# tests/test_models.py
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from finance.models import Category, SavingsGoal, Transaction

User = get_user_model()


@pytest.mark.django_db
def test_remaining_amount_property():
    """
    SavingsGoal.remaining_amount should return target − current.
    """
    user = User.objects.create_user(email="goal@example.com", password="secret")

    goal = SavingsGoal.objects.create(
        user=user,
        name="Vacation 2026",
        target_amount=Decimal("1500.00"),
        current_amount=Decimal("400.00"),
    )

    assert goal.remaining_amount == Decimal("1100.00")


@pytest.mark.django_db
def test_transaction_str():
    """
    __str__ for Transaction should be human-friendly.
    """
    user = User.objects.create_user(email="tx@example.com", password="secret")
    cat = Category.objects.create(name="Food", user=user)

    tx = Transaction.objects.create(
        user=user,
        category=cat,
        type=Transaction.Type.EXPENSE,
        amount=Decimal("12.34"),
        date="2025-08-01",
        description="Tacos 🌮",
    )

    assert "Tacos" in str(tx)
    assert "12.34" in str(tx)
