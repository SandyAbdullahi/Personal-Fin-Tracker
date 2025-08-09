# finance/models.py
from __future__ import annotations

from datetime import date
from decimal import Decimal

from dateutil.rrule import rrulestr
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum, UniqueConstraint
from django.utils import timezone
from django_extensions.db.models import TimeStampedModel


# ─────────────────────────────── Categories ────────────────────────────────
class Category(TimeStampedModel):
    name = models.CharField(max_length=64)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories",
        null=True,
        blank=True,
    )

    class Meta:
        constraints = [UniqueConstraint(fields=["user", "name"], name="unique_category_per_user")]

    def __str__(self) -> str:  # pragma: no cover
        return self.name


# ─────────────────────────────── Transactions ──────────────────────────────
class Transaction(TimeStampedModel):
    class Type(models.TextChoices):
        INCOME = "IN", "Income"
        EXPENSE = "EX", "Expense"

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=2, choices=Type.choices)
    description = models.CharField(max_length=128, blank=True)
    date = models.DateField()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions",
        null=True,
        blank=True,
    )

    # link back to a transfer when this row was produced by a Transfer action
    transfer = models.ForeignKey(
        "Transfer",
        on_delete=models.CASCADE,
        related_name="transactions",
        null=True,
        blank=True,
    )

    def __str__(self) -> str:  # pragma: no cover
        desc = f"{self.description} " if self.description else ""
        sign = "+" if self.type == self.Type.INCOME else "-"
        value = f"{sign}{self.amount:.2f}"
        return f"{desc}{value} {self.category}"


# ───────────────────────────── Savings Goals ───────────────────────────────
class SavingsGoal(TimeStampedModel):
    name = models.CharField(max_length=64)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    target_date = models.DateField(blank=True, null=True)

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


# ─────────────────────── Recurring Transactions ────────────────────────────
class RecurringTransaction(models.Model):
    """
    Blueprint for posting future `Transaction`s automatically.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recurrings",
    )
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="recurrings")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=2, choices=[("IN", "Income"), ("EX", "Expense")])
    description = models.CharField(max_length=255, blank=True)

    # schedule / cadence
    rrule = models.CharField(max_length=200)
    next_occurrence = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    # housekeeping
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "description", "rrule")
        ordering = ("next_occurrence",)

    # validation
    def clean(self):
        super().clean()
        try:
            rrulestr(self.rrule, dtstart=date.today())
        except (ValueError, TypeError):
            raise ValidationError({"rrule": "Invalid RRULE string."})

        if self.next_occurrence < timezone.localdate():
            raise ValidationError({"next_occurrence": "Date cannot be in the past."})

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.user} → {self.amount} " f"{self.get_type_display()} @ {self.rrule}"


# ───────────────────────────────── Budgets ──────────────────────────────────
class Budget(TimeStampedModel):
    """
    A spending envelope for a single category & period.
    List views annotate the query-set, but detail views (and factory_boy)
    rely on these fallback properties.
    """

    PERIODS = [("M", "Monthly"), ("Y", "Yearly")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="budgets")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="budgets")
    limit = models.DecimalField(max_digits=10, decimal_places=2)
    period = models.CharField(max_length=1, choices=PERIODS, default="M")

    class Meta:
        constraints = [UniqueConstraint(fields=["user", "category", "period"], name="unique_budget_per_period")]
        ordering = ("-created",)

    # ───────────────────────── display ───────────────────────── #
    def __str__(self) -> str:  # pragma: no cover
        return f"{self.category} – {self.limit} ({self.get_period_display()})"

    # ─────────────────── computed helpers ────────────────────── #
    @property
    def amount_spent(self) -> Decimal:
        """Monthly expenses for this user *and* category."""
        today = timezone.localdate()
        return Transaction.objects.filter(
            user=self.user,
            category=self.category,
            type="EX",
            date__year=today.year,
            date__month=today.month,
        ).aggregate(t=Sum("amount"))["t"] or Decimal("0.00")

    @amount_spent.setter  # allows BudgetFactory(spent=…)
    def amount_spent(self, _):  # value ignored
        pass

    @property
    def remaining(self) -> Decimal:
        return self.limit - self.amount_spent

    @remaining.setter  # lets Django assign during annotation
    def remaining(self, _):
        pass

    @property
    def percent_used(self) -> float:
        return float(self.amount_spent / self.limit * 100) if self.limit else 0.0

    @percent_used.setter
    def percent_used(self, _):
        pass

    # alias that factory_boy uses
    @property
    def spent(self) -> Decimal:
        return self.amount_spent

    @spent.setter  # same dummy setter
    def spent(self, _):
        pass


# ───────────────────────────────── Debts and Payments ──────────────────────────────────
class Debt(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="debts")
    name = models.CharField(max_length=64)
    principal = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="% per annum")
    minimum_payment = models.DecimalField(max_digits=10, decimal_places=2)
    opened_date = models.DateField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ("-created",)

    @property
    def balance(self):
        paid = self.payments.aggregate(t=Sum("amount"))["t"] or Decimal("0.00")
        return self.principal - paid


class Payment(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments")
    debt = models.ForeignKey(Debt, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    memo = models.CharField(max_length=128, blank=True)


# ─────────────────────────────── Transfers ────────────────────────────────
class Transfer(TimeStampedModel):
    """
    Move money between two categories by creating a paired Transaction:
      • source  → Expense (EX)   –amount
      • dest    → Income  (IN)   +amount
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transfers")
    source_category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="transfers_out")
    destination_category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="transfers_in")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ("-date", "-id")

    def clean(self):
        if self.source_category_id and self.destination_category_id:
            if self.source_category_id == self.destination_category_id:
                raise ValidationError({"destination_category": "Source and destination must differ."})

    def __str__(self) -> str:  # pragma: no cover
        return f"Transfer {self.amount} {self.source_category} → {self.destination_category} on {self.date}"
