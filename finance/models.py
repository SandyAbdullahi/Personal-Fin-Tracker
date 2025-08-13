# finance/models.py
from __future__ import annotations

from datetime import date
from decimal import Decimal

from dateutil.rrule import rrulestr
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Max, Sum, UniqueConstraint
from django.utils import timezone
from django_extensions.db.models import TimeStampedModel


# ─────────────────────────── Per-user sequence mixin ───────────────────────────
class PerUserSequenceMixin(models.Model):
    """
    Adds a per-user auto-incrementing `local_id` that starts at 1 for each user.
    Assumes the model has a FK named `user`.
    """

    local_id = models.PositiveIntegerField(editable=False, null=True)

    class Meta:
        abstract = True

    def _next_local_id(self) -> int:
        agg = self.__class__.objects.filter(user=self.user).aggregate(m=Max("local_id"))
        return (agg["m"] or 0) + 1

    def save(self, *args, **kwargs):
        # Assign only on create
        if self._state.adding and self.local_id is None:
            # Tiny retry loop to handle a rare race condition
            for _ in range(3):
                try:
                    with transaction.atomic():
                        self.local_id = self._next_local_id()
                        return super().save(*args, **kwargs)
                except Exception:
                    # another concurrent insert likely grabbed the same number
                    self.local_id = None
        return super().save(*args, **kwargs)


# ───────────────────────────────── Categories ─────────────────────────────────
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


# ──────────────────────────────── Transactions ────────────────────────────────
class Transaction(PerUserSequenceMixin, TimeStampedModel):
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

    class Meta:
        constraints = [
            UniqueConstraint(fields=["user", "local_id"], name="uniq_tx_user_local_id"),
        ]

    def __str__(self) -> str:  # pragma: no cover
        desc = f"{self.description} " if self.description else ""
        sign = "+" if self.type == self.Type.INCOME else "-"
        value = f"{sign}{self.amount:.2f}"
        return f"{desc}{value} {self.category}"


# ───────────────────────────────── Savings Goals ──────────────────────────────
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


# ───────────────────────────── Recurring Transactions ─────────────────────────
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

    def clean(self):
        super().clean()
        try:
            rrulestr(self.rrule, dtstart=date.today())
        except (ValueError, TypeError):
            raise ValidationError({"rrule": "Invalid RRULE string."})

        if self.next_occurrence < timezone.localdate():
            raise ValidationError({"next_occurrence": "Date cannot be in the past."})

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.user} → {self.amount} {self.get_type_display()} @ {self.rrule}"


# ─────────────────────────────────── Budgets ──────────────────────────────────
class Budget(PerUserSequenceMixin, TimeStampedModel):
    """
    A spending envelope for a single category & period.
    List views annotate the queryset; these properties act as a fallback
    for detail views and factories.
    """

    PERIODS = [("M", "Monthly"), ("Y", "Yearly")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="budgets")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="budgets")
    limit = models.DecimalField(max_digits=10, decimal_places=2)
    period = models.CharField(max_length=1, choices=PERIODS, default="M")

    class Meta:
        constraints = [
            UniqueConstraint(fields=["user", "category", "period"], name="unique_budget_per_period"),
            UniqueConstraint(fields=["user", "local_id"], name="uniq_budget_user_local_id"),
        ]
        ordering = ("-created",)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.category} – {self.limit} ({self.get_period_display()})"

    # Fallback computed helpers (detail view / admin / tests)
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

    @amount_spent.setter
    def amount_spent(self, _):  # allow assignment during annotation/factory use
        pass

    @property
    def remaining(self) -> Decimal:
        return self.limit - self.amount_spent

    @remaining.setter
    def remaining(self, _):
        pass

    @property
    def percent_used(self) -> float:
        return float(self.amount_spent / self.limit * 100) if self.limit else 0.0

    @percent_used.setter
    def percent_used(self, _):
        pass

    # alias some factories expect
    @property
    def spent(self) -> Decimal:
        return self.amount_spent

    @spent.setter
    def spent(self, _):
        pass

    def clean(self):
        super().clean()
        if self.category_id and self.user_id and self.category.user_id != self.user_id:
            raise ValidationError({"category": "Category does not belong to this user."})


# ───────────────────────────────── Debts & Payments ───────────────────────────
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


# ─────────────────────────────────── Transfers ────────────────────────────────
class Transfer(PerUserSequenceMixin, TimeStampedModel):
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
        constraints = [
            UniqueConstraint(fields=["user", "local_id"], name="uniq_transfer_user_local_id"),
        ]
        ordering = ("-date", "-id")

    def clean(self):
        if self.source_category_id and self.destination_category_id:
            if self.source_category_id == self.destination_category_id:
                raise ValidationError({"destination_category": "Source and destination must differ."})

    def __str__(self) -> str:  # pragma: no cover
        return f"Transfer {self.amount} {self.source_category} → {self.destination_category} on {self.date}"
