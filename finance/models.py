# finance/models.py
from django.conf import settings
from django.db import models
from django.utils import timezone


class Category(models.Model):
    """
    A category belongs to one user so that two users can each have
    their own “Food”, “Salary”, etc. without collisions.
    """
    user = models.ForeignKey(                       # ← NEW
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories",
    )
    name = models.CharField(max_length=50)

    class Meta:
        unique_together = ("user", "name")          # one name per user
        ordering = ("name",)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    INCOME = "IN"
    EXPENSE = "EX"
    TYPE_CHOICES = [(INCOME, "Income"), (EXPENSE, "Expense")]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)  # keep data safe
    date = models.DateField()
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.get_type_display()} - {self.amount}"


class SavingsGoal(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="goals"
    )
    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    @property
    def amount_saved(self):
        total = (
            self.user.transactions.filter(
                type="IN",
                category__name="Savings",
                date__lte=timezone.now().date(),
            ).aggregate(models.Sum("amount"))["amount__sum"]
            or 0
        )
        return total

    def __str__(self):
        return f"{self.name} ({self.user.email})"
