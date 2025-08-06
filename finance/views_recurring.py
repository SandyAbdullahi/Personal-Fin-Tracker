# finance/views_recurring.py
from datetime import date, datetime, time

from dateutil.rrule import rrulestr
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from finance.models import RecurringTransaction, Transaction


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def post_due_recurring_transactions(request):
    """
    Create Transaction rows for every RecurringTransaction due today.
    """

    today = date.today()
    count = 0

    recurrings = (
        RecurringTransaction.objects.filter(active=True, user=request.user, next_occurrence__lte=today)
        .select_related("user", "category")
        .order_by("next_occurrence")
    )

    for r in recurrings:
        # keep looping while this item is still due *today*
        while r.active and r.next_occurrence and r.next_occurrence <= today:

            # 1️⃣ post the real Transaction
            Transaction.objects.create(
                user=r.user,
                category=r.category,
                amount=r.amount,
                type=r.type,
                description=r.description,
                date=r.next_occurrence,
            )
            count += 1

            # 2️⃣ work with DATETIME when talking to rrule
            current_dt = datetime.combine(r.next_occurrence, time.min)
            rule = rrulestr(r.rrule, dtstart=current_dt)

            next_dt = rule.after(current_dt)  # - returns datetime
            next_date = next_dt.date() if next_dt else None  # ☞ normalise

            # 3️⃣ update or deactivate
            if next_date is None or (r.end_date and next_date > r.end_date):
                r.active = False
            else:
                r.next_occurrence = next_date

            r.save(update_fields=["next_occurrence", "active"])

    return Response({"posted": count, "date": str(today)})
