# tests/test_category_model.py
import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from finance.models import Category

User = get_user_model()


@pytest.mark.django_db
def test_category_string_representation():
    """
    __str__ should return the category's name.
    """
    user = User.objects.create_user(email="cat@example.com", password="secret")
    cat = Category.objects.create(name="Groceries", user=user)
    assert str(cat) == "Groceries"


@pytest.mark.django_db
def test_category_name_unique_per_user():
    """
    Users shouldn’t be able to create two categories with the same name.
    """
    user = User.objects.create_user(email="cat@example.com", password="secret")
    Category.objects.create(name="Rent", user=user)

    with pytest.raises(IntegrityError):
        # Attempting to save a second “Rent” for the *same* user.
        Category.objects.create(name="Rent", user=user)


@pytest.mark.django_db
def test_same_name_allowed_for_different_users():
    """
    The uniqueness constraint is per-user, so different users can share names.
    """
    user1 = User.objects.create_user(email="one@example.com", password="secret")
    user2 = User.objects.create_user(email="two@example.com", password="secret")

    Category.objects.create(name="Utilities", user=user1)  # ok
    Category.objects.create(name="Utilities", user=user2)  # also ok

    assert Category.objects.filter(name="Utilities").count() == 2
