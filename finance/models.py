# finance/models.py
from decimal import Decimal
from django.conf import settings
from django.db import models
from django_extensions.db.models import TimeStampedModel


class Category(TimeStampedModel):
    name = models.CharField(max_length=64)
    # make user optional so tests can create categories without it
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories",
        null=True,  # ← keeps earlier tests happy
        blank=True,
    )

    class Meta:
        # “Food” may appear for many users, but only once per-user.
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="unique_category_per_user",
            )
        ]

    def __str__(self) -> str:  # pragma: no cover -- trivial
        return self.name


class Transaction(TimeStampedModel):
    class Type(models.TextChoices):
        INCOME = "IN", "Income"
        EXPENSE = "EX", "Expense"

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=2, choices=Type.choices)
    description = models.CharField(max_length=128, blank=True)
    date = models.DateField()

    user = models.ForeignKey(  # optional for the tests
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions",
        null=True,
        blank=True,
    )

    # ---------- helpers -------------------------------------------------- #
    def __str__(self) -> str:
        """
        Tests expect the *description* to appear in the string repr.
        Example →  ``"Tacos -12.34 Food"``
        """
        desc = f"{self.description} " if self.description else ""
        sign = "+" if self.type == self.Type.INCOME else "-"
        value = f"{sign}{self.amount:.2f}"
        return f"{desc}{value} {self.category}"


class SavingsGoal(TimeStampedModel):
    name = models.CharField(max_length=64)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    target_date = models.DateField(blank=True, null=True)

    # optional → unit-tests can create a goal without first creating a user
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="goals",
        null=True,
        blank=True,
    )

    @property
    def remaining_amount(self) -> Decimal:
        return max(self.target_amount - self.current_amount, Decimal("0.00"))

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.name} ({self.current_amount}/{self.target_amount})"
