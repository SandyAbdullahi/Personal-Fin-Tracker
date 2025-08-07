import django_filters as filters

from .models import Budget, Category, SavingsGoal, Transaction


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


# ───────────────────────── Budget ──────────────────────────
class BudgetFilter(filters.FilterSet):
    """
    Allow the client to:
      • restrict to a `category`  (?category=<id>)
      • restrict to a `period`    (?period=M)
      • search for budgets whose limit is >= / <= a value
    """

    min_limit = filters.NumberFilter(field_name="limit", lookup_expr="gte")
    max_limit = filters.NumberFilter(field_name="limit", lookup_expr="lte")

    class Meta:
        model = Budget
        fields = ["category", "period", "min_limit", "max_limit"]
