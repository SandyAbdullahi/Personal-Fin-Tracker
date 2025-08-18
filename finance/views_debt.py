# finance/views_debt.py
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from .models import Debt, Payment
from .permissions import IsOwnerOrReadOnly
from .serializers import DebtSerializer, PaymentSerializer


class DebtViewSet(viewsets.ModelViewSet):
    """
    /api/finance/debts/
    """

    serializer_class = DebtSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["category"]
    ordering_fields = ["opened_date", "balance", "principal", "minimum_payment"]
    ordering = ["-opened_date"]

    def get_queryset(self):
        # Only the current user's debts
        return Debt.objects.filter(user=self.request.user).order_by(*self.ordering)

    def perform_create(self, serializer):
        # Stamp the user on create
        serializer.save(user=self.request.user)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    /api/finance/payments/
    Supports filtering by `?debt=<id>` (and always scoped to the current user).
    """

    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["debt"]
    ordering_fields = ["date", "amount", "id"]
    ordering = ["-date", "-id"]

    def get_queryset(self):
        """
        Only payments belonging to the current user.
        Additionally honor `?debt=<id>` explicitly so clients can fetch
        just one debt's payments (works alongside DjangoFilterBackend).
        """
        qs = Payment.objects.filter(user=self.request.user).order_by(*self.ordering)

        debt_id = self.request.query_params.get("debt")
        if debt_id:
            qs = qs.filter(debt_id=debt_id)

        return qs

    def perform_create(self, serializer):
        """
        Ensure the payment is being created for a debt owned by the current user
        and stamp the `user` field.
        """
        debt = serializer.validated_data.get("debt")
        if not debt or debt.user_id != self.request.user.id:
            raise PermissionDenied("You cannot add a payment to this debt.")
        serializer.save(user=self.request.user)
