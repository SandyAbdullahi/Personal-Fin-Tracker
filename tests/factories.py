import factory
from django.contrib.auth import get_user_model
from finance.models import Category, Transaction, SavingsGoal

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
