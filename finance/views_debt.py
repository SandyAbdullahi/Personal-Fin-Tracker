# finance/views_debt.py
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Debt, Payment
from .permissions import IsOwnerOrReadOnly
from .serializers import DebtSerializer, PaymentSerializer


class DebtViewSet(viewsets.ModelViewSet):
    serializer_class = DebtSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["category"]
    ordering_fields = ["opened_date", "balance"]
    ordering = ["-opened_date"]

    def get_queryset(self):
        return Debt.objects.filter(user=self.request.user)


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["debt"]
    ordering_fields = ["date", "amount"]
    ordering = ["-date"]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)
