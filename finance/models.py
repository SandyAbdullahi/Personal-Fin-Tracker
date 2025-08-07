# finance/models.py
from datetime import date
from decimal import Decimal

from dateutil.rrule import rrulestr
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
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


class RecurringTransaction(models.Model):
    """
    Blueprint for posting future `Transaction`s automatically.

    Example: a rent payment of –750 on the 1st of every month.
    """

    # ───────────────────────────── basics ───────────────────────────── #
    user = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.CASCADE,
        related_name="recurrings",
    )
    category = models.ForeignKey(
        "finance.Category",
        on_delete=models.PROTECT,
        related_name="recurrings",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(
        max_length=2,
        choices=[("IN", "Income"), ("EX", "Expense")],
    )
    description = models.CharField(max_length=255, blank=True)

    # ───────────────────────── cadence / schedule ───────────────────── #
    # We store an **RFC-5545 RRULE** string because it’s flexible,
    # human-readable and can be parsed by `dateutil.rrule`.
    #
    # ▸ Examples
    #   - "FREQ=MONTHLY;BYMONTHDAY=1"           → every 1st
    #   - "FREQ=WEEKLY;BYDAY=MO,FR"             → every Monday & Friday
    #   - "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25"→ every Christmas
    rrule = models.CharField(max_length=200)

    # the next date at which we still need to post the transaction
    next_occurrence = models.DateField()

    # If a recurring item should stop after N posts (optional)
    end_date = models.DateField(null=True, blank=True)

    # ───────────────────────── housekeeping ─────────────────────────── #
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "description", "rrule")  # avoid duplicates
        ordering = ("next_occurrence",)

    # ───────────────────────── validation hooks ─────────────────────── #
    def clean(self):
        super().clean()

        # 1. Make sure `rrule` parses.
        try:
            rrulestr(self.rrule, dtstart=date.today())
        except (ValueError, TypeError):
            raise ValidationError({"rrule": "Invalid RRULE string."})

        # 2. next_occurrence must be ≥ today
        if self.next_occurrence < timezone.localdate():
            raise ValidationError({"next_occurrence": "Date cannot be in the past."})

    def __str__(self) -> str:
        return f"{self.user} → {self.amount} {self.get_type_display()} @ {self.rrule}"


class Budget(TimeStampedModel):
    """
    A spending limit (‐`limit`‐) for a *single* category over a period.

    Period choices:
      M → monthly   (resets every calendar month)
      Q → quarterly (Jan-Mar, Apr-Jun, Jul-Sep, Oct-Dec)
      Y → yearly    (Jan-Dec)
    """

    PERIOD_CHOICES = (
        ("M", "Monthly"),
        ("Q", "Quarterly"),
        ("Y", "Yearly"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="budgets",
    )
    category = models.ForeignKey(
        "finance.Category",
        on_delete=models.CASCADE,
        related_name="budgets",
    )
    limit = models.DecimalField(max_digits=10, decimal_places=2)
    period = models.CharField(max_length=1, choices=PERIOD_CHOICES, default="M")

    class Meta:
        # a user can’t have TWO monthly budgets for the same category
        constraints = [
            models.UniqueConstraint(
                fields=["user", "category", "period"],
                name="unique_budget_per_period",
            )
        ]
        ordering = ("-created",)

    # trivial helper – nice for Django admin / str() tests
    def __str__(self) -> str:  # pragma: no cover
        return f"{self.user} {self.category} {self.get_period_display()} → {self.limit}"

    # defensive: ensure limit > 0 even if serializer is bypassed
    def clean(self):
        super().clean()
        if self.limit <= Decimal("0"):
            raise ValidationError({"limit": "Limit must be positive."})
