from django.db.models import Sum, F
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwnerOrReadOnly
from rest_framework.response import Response
from .models import Transaction

from .models import Category, SavingsGoal
from .serializers import (
    CategorySerializer,
    TransactionSerializer,
    SavingsGoalSerializer,
)


# ────────────────────────────────────────────────
#   Category CRUD
# ────────────────────────────────────────────────
class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ────────────────────────────────────────────────
#   Transaction CRUD (user-scoped)
# ────────────────────────────────────────────────
class TransactionViewSet(viewsets.ModelViewSet):
    """
    Standard CRUD endpoint backed by TransactionSerializer.
    Only returns the requesting user’s own transactions.
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_success_headers(self, data):
        return {}


# ────────────────────────────────────────────────
#   Savings Goal CRUD (user-scoped)
# ────────────────────────────────────────────────
class SavingsGoalViewSet(viewsets.ModelViewSet):
    serializer_class = SavingsGoalSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return SavingsGoal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ────────────────────────────────────────────────
#   Finance Summary Endpoint
# ────────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def summary(request):
    """
    Returns total income, total expenses, per-category totals,
    and savings-goal progress for the authenticated user.

    Optional query params:
      ?start=YYYY-MM-DD   filter transactions from this date
      ?end=YYYY-MM-DD     filter up to this date
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

    by_category = (
        qs.values(name=F("category__name"))  # ← valid expression alias
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )

    goal_data = [
        {
            "id": g.id,
            "name": g.name,
            "target": g.target_amount,
            "saved": g.amount_saved,
            "percent": (
                round((g.amount_saved / g.target_amount) * 100, 1)
                if g.target_amount
                else 0
            ),
            "deadline": g.deadline,
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
