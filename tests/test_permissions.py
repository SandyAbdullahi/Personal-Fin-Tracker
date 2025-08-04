# tests/test_permissions.py
import pytest
from django.urls import reverse
from rest_framework import status
from tests.factories import (
    UserFactory, CategoryFactory, TransactionFactory, SavingsGoalFactory
)

@pytest.mark.django_db
@pytest.mark.parametrize("factory_name, url_name", [
    ("category", "categories-list"),
    ("transaction", "transactions-list"),
    ("savingsgoal", "goals-list"),
])
def test_user_cannot_see_others(factory_name, url_name, api_client):
    owner = UserFactory()
    intruder = UserFactory()

    obj = {
        "category": CategoryFactory,
        "transaction": TransactionFactory,
        "savingsgoal": SavingsGoalFactory,
    }[factory_name](user=owner)

    api_client.force_authenticate(intruder)
    list_resp = api_client.get(reverse(url_name))
    detail_resp = api_client.get(
        reverse(url_name.replace("list", "detail"), args=[obj.pk])
    )

    assert obj.pk not in [o["id"] for o in list_resp.data]
    assert detail_resp.status_code == status.HTTP_404_NOT_FOUND
