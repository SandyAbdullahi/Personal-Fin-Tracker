# finance/views.py
from decimal import Decimal

from django.db.models import Case, DecimalField, ExpressionWrapper, F, FloatField, OuterRef, Subquery, Sum, Value, When
from django.db.models.functions import Coalesce
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import BudgetFilter, CategoryFilter, SavingsGoalFilter, TransactionFilter
from .models import Budget, Category, SavingsGoal, Transaction, Transfer
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    BudgetSerializer,
    CategorySerializer,
    SavingsGoalSerializer,
    TransactionSerializer,
    TransferSerializer,
)


# ─────────────────────────────── Category CRUD ────────────────────────────────
class CategoryViewSet(viewsets.ModelViewSet):
    """CRUD actions for categories (per-user)."""

    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    filter_backends = [DjangoFilterBackend]
    filterset_class = CategoryFilter

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ───────────────────────────── Transaction CRUD ───────────────────────────────
class TransactionViewSet(viewsets.ModelViewSet):
    """
    Standard CRUD endpoint for `Transaction`.
    Default ordering: newest first (id ↓).
    """

    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = TransactionFilter
    search_fields = ["description"]
    ordering_fields = ["date", "amount", "id"]
    ordering = ("-id",)  # deterministic default

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by(*self.ordering)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ─────────────────────────── Savings-Goal CRUD ───────────────────────────────
class SavingsGoalViewSet(viewsets.ModelViewSet):
    """CRUD for `SavingsGoal` (name filter supported)."""

    serializer_class = SavingsGoalSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    filter_backends = [DjangoFilterBackend]
    filterset_class = SavingsGoalFilter

    def get_queryset(self):
        return SavingsGoal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ───────────────────────────── Finance summary ───────────────────────────────
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def summary(request):
    """
    Aggregate view returning:
      • total income / expenses
      • totals per category
      • progress of each savings goal
    Optional query params:
        ?start=YYYY-MM-DD   – from date
        ?end=YYYY-MM-DD     – up to date
    """
    qs = Transaction.objects.filter(user=request.user)

    start = request.GET.get("start")
    end = request.GET.get("end")
    if start:
        qs = qs.filter(date__gte=start)
    if end:
        qs = qs.filter(date__lte=end)

    income_total = qs.filter(type="IN").aggregate(t=Sum("amount"))["t"] or 0
    expense_total = qs.filter(type="EX").aggregate(t=Sum("amount"))["t"] or 0

    by_category = qs.values(name=F("category__name")).annotate(total=Sum("amount")).order_by("-total")

    goal_data = [
        {
            "id": g.id,
            "name": g.name,
            "target": g.target_amount,
            "saved": g.current_amount,
            "percent": (round((g.current_amount / g.target_amount) * 100, 1) if g.target_amount else 0),
            "deadline": g.target_date,
        }
        for g in request.user.goals.all()
    ]

    return Response(
        {
            "income_total": income_total,
            "expense_total": expense_total,
            "by_category": list(by_category),
            "goals": goal_data,
        }
    )


# ─────────────────────────────── Budget CRUD ────────────────────────────────
class BudgetViewSet(viewsets.ModelViewSet):
    """
    CRUD for a user-scoped `Budget`.
    The queryset is annotated with:
      • spent        – total expenses in the current month
      • remaining    – limit − spent
      • percent_used – (spent / limit) × 100
    """

    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = BudgetFilter
    ordering_fields = ["created", "limit", "spent", "remaining", "percent_used"]
    ordering = ("-created",)

    # ------------------------------------------------------------------ #
    def get_queryset(self):
        user = self.request.user
        today = timezone.localdate()

        # sub-query → total expenses in this category for the current month
        monthly_total = (
            Transaction.objects.filter(
                user=OuterRef("user"),
                category=OuterRef("category"),
                type="EX",
                date__year=today.year,
                date__month=today.month,
            )
            .values("category")
            .annotate(total=Sum("amount"))
            .values("total")[:1]
        )

        # one reusable expression
        spent_expr = Coalesce(
            Subquery(
                monthly_total,
                output_field=DecimalField(max_digits=10, decimal_places=2),
            ),
            Value(Decimal("0.00")),
        )

        return Budget.objects.filter(user=user).annotate(
            spent=spent_expr,  # alias for ordering
            remaining=ExpressionWrapper(
                F("limit") - spent_expr,
                output_field=DecimalField(max_digits=10, decimal_places=2),
            ),
            percent_used=Case(
                When(limit=0, then=Value(0.0)),
                default=ExpressionWrapper(
                    spent_expr * Value(Decimal("100.00")) / F("limit"),
                    output_field=FloatField(),
                ),
                output_field=FloatField(),
            ),
        )

    # ------------------------------------------------------------------ #
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ─────────────────────────────── Transfer Views ────────────────────────────────
class TransferViewSet(viewsets.ModelViewSet):
    serializer_class = TransferSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["source_category", "destination_category", "date"]
    ordering_fields = ["date", "amount", "id"]
    ordering = ("-date", "-id")

    def get_queryset(self):
        return Transfer.objects.filter(user=self.request.user)
