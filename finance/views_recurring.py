# finance/views_recurring.py
from __future__ import annotations

from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import RecurringTransaction, Transaction
from .permissions import IsOwnerOrReadOnly
from .serializers import RecurringTransactionSerializer


class RecurringTransactionViewSet(viewsets.ModelViewSet):
    """CRUD for recurring items, scoped to the current user."""

    serializer_class = RecurringTransactionSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return RecurringTransaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def post_due_recurring_transactions(request):
    from datetime import datetime

    from dateutil.rrule import rrulestr
    from django.utils import timezone

    today = timezone.localdate()
    posted = 0

    due = RecurringTransaction.objects.filter(user=request.user, active=True, next_occurrence__lte=today)

    for r in due:
        Transaction.objects.create(
            user=request.user,
            category=r.category,
            amount=r.amount,
            type=r.type,
            description=r.description,
            date=r.next_occurrence,
        )
        posted += 1

        # compute next occurrence safely (datetime vs date)
        dtstart = datetime.combine(r.next_occurrence, datetime.min.time())
        rule = rrulestr(r.rrule, dtstart=dtstart)
        next_dt = rule.after(dtstart, inc=False)

        if next_dt is None:
            r.active = False
        else:
            nx = next_dt.date()
            if r.end_date and nx > r.end_date:
                r.active = False
            else:
                r.next_occurrence = nx

        r.save(update_fields=["next_occurrence", "active"])

    return Response({"posted": posted, "date": str(today)})
