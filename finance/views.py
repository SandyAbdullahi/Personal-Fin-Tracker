from rest_framework import viewsets, permissions
from rest_framework.response import Response

from .models import Transaction, Category
from .serializers import TransactionSerializer, CategorySerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['type', 'category', 'date']  # gives ?type=EX&category=1&date=2025-07-29

    def get_queryset(self):
        return self.request.user.transactions.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def summary(request):
    qs = request.user.transactions.all()

    start = request.GET.get('start')
    end = request.GET.get('end')
    if start: qs = qs.filter(date__gte=start)
    if end:   qs = qs.filter(date__lte=end)

    income_total = qs.filter(type='IN').aggregate(total=Sum('amount'))['total'] or 0
    expense_total = qs.filter(type='EX').aggregate(total=Sum('amount'))['total'] or 0

    by_category = (
        qs.values('category__name')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    return Response({
        "income_total": income_total,
        "expense_total": expense_total,
        "by_category": list(by_category)
    })
