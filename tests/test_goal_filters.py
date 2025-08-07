import pytest
from django.urls import reverse

from tests.factories import SavingsGoalFactory, UserFactory


@pytest.mark.django_db
def test_goal_name_filter(api_client):
    user = UserFactory()
    other = UserFactory()
    # cat = CategoryFactory(user=user)

    # user’s two goals
    SavingsGoalFactory(user=user, name="House deposit")
    SavingsGoalFactory(user=user, name="Holiday fund")
    # someone else’s goal
    SavingsGoalFactory(user=other, name="House deposit")

    api_client.force_authenticate(user)
    url = reverse("finance:goals-list") + "?name__icontains=house"
    resp = api_client.get(url)

    names = [g["name"] for g in resp.data["results"]]
    assert names == ["House deposit"]  # only the owner’s match
