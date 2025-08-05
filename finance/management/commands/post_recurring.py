import datetime as dt

from dateutil.rrule import rrulestr
from django.core.management.base import BaseCommand
from django.db import transaction as db_tx

from finance.models import RecurringTransaction, Transaction


class Command(BaseCommand):
    help = "Create Transaction rows for every RecurringTransaction due today."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    # ------------------------------------------------------------------ #
    def handle(self, *args, dry_run=False, **kwargs):
        today = dt.date.today()
        due_qs = (
            RecurringTransaction.objects.filter(active=True, next_occurrence__lte=today)
            .select_related("user", "category")
            .order_by("next_occurrence")
        )

        if not due_qs.exists():
            self.stdout.write(self.style.SUCCESS("Nothing due today."))
            return

        with db_tx.atomic():
            for r in due_qs:
                while r.active and r.next_occurrence <= today:
                    self._post_once(r, dry_run)

                    # ensure it's a plain *date* before looping again
                    if isinstance(r.next_occurrence, dt.datetime):
                        r.next_occurrence = r.next_occurrence.date()

            if dry_run:
                db_tx.set_rollback(True)

        self.stdout.write(self.style.SUCCESS("✓ Finished."))
        if dry_run:
            self.stdout.write(self.style.WARNING(" (dry-run: rolled back)"))

    # ------------------------------------------------------------------ #
    def _post_once(self, r: RecurringTransaction, dry_run: bool):
        if not dry_run:
            Transaction.objects.create(
                user=r.user,
                category=r.category,
                amount=r.amount,
                type=r.type,
                description=r.description,
                date=r.next_occurrence,
            )

        # ----- make sure dtstart is a datetime ------------------------
        dt_start = (
            r.next_occurrence
            if isinstance(r.next_occurrence, dt.datetime)
            else dt.datetime.combine(r.next_occurrence, dt.time.min)
        )

        rule = rrulestr(r.rrule, dtstart=dt_start)
        next_dt = rule.after(dt_start)  # datetime | None
        next_date = next_dt.date() if next_dt else None

        if next_date is None or (r.end_date and next_date > r.end_date):
            r.active = False
        else:
            r.next_occurrence = next_date  # store as *date*

        if not dry_run:
            r.save(update_fields=["next_occurrence", "active"])
