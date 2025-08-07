import django_filters as filters

from .models import Category, SavingsGoal, Transaction


# ───────────────────────── Category ──────────────────────────
class CategoryFilter(filters.FilterSet):
    class Meta:
        model = Category
        fields = {"name": ["icontains"]}


# ──────────────────────── Transaction ────────────────────────
class TransactionFilter(filters.FilterSet):
    class Meta:
        model = Transaction
        fields = {
            "category": ["exact"],
            "type": ["exact"],
            "amount": ["gte", "lte"],
            "date": ["gte", "lte"],
            "description": ["icontains"],
        }


# ─────────────────────── SavingsGoal ────────────────────────
class SavingsGoalFilter(filters.FilterSet):
    """
    Accepts `?name__icontains=` just like the failing test expects.
    """

    class Meta:
        model = SavingsGoal
        fields = {"name": ["icontains"]}
