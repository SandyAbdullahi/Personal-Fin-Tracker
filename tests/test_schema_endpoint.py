import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_openapi_schema_available():
    client = APIClient()
    resp = client.get(reverse("schema"))  # /api/schema/
    assert resp.status_code == 200
    assert resp.data["info"]["title"] == "Personal Finance Tracker API"
