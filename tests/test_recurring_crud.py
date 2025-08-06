# tests/test_recurring_crud.py
import pytest
from django.urls import reverse
from rest_framework import status

from tests.factories import CategoryFactory, UserFactory

REC_LIST = "finance:recurrings-list"


@pytest.mark.django_db
def test_user_can_create_and_list_recurring(api_client):
    user = UserFactory()
    cat = CategoryFactory(user=user)
    api_client.force_authenticate(user)

    payload = {
        "category_id": cat.id,
        "amount": "123.45",
        "type": "EX",
        "description": "Gym",
        "rrule": "FREQ=MONTHLY;BYMONTHDAY=10",
        "next_occurrence": "2025-10-10",
    }
    resp = api_client.post(reverse(REC_LIST), payload, format="json")
    assert resp.status_code == status.HTTP_201_CREATED

    list_resp = api_client.get(reverse(REC_LIST))
    assert list_resp.data["count"] == 1
    assert list_resp.data["results"][0]["description"] == "Gym"
