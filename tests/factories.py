from decimal import Decimal

import factory
from django.contrib.auth import get_user_model

from finance.models import Budget, Category, Debt, Payment, SavingsGoal, Transaction

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass")


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Cat{n}")
    user = factory.SubFactory(UserFactory)


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)
    type = "EX"
    amount = 50
    date = factory.Faker("date_this_year")
    description = "lunch"


class SavingsGoalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SavingsGoal

    user = factory.SubFactory(UserFactory)
    name = "Vacation"
    target_amount = 1000
    current_amount = 100


class BudgetFactory(factory.django.DjangoModelFactory):
    """
    Creates a Budget that’s automatically linked to:
      • the same `user` as its Category
      • a sensible default limit (KES 1 000) and a monthly period
    Override any field in your tests, e.g.:
        BudgetFactory(limit=500, period="W")
    """

    class Meta:
        model = Budget
        django_get_or_create = ("user", "category", "period")

    # relations
    category = factory.SubFactory(CategoryFactory)
    user = factory.LazyAttribute(lambda obj: obj.category.user)

    # simple fields
    limit = Decimal("1000.00")
    period = "M"  # "M" (Monthly) / "W" / "Y" – adjust to your choices


class DebtFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Debt

    user = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f"Debt{n}")
    principal = Decimal("1000")
    interest_rate = Decimal("5")
    minimum_payment = Decimal("50")


class PaymentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Payment

    user = factory.SubFactory(UserFactory)
    debt = factory.SubFactory(DebtFactory)
    amount = Decimal("100")
    date = factory.Faker("date_this_year")
