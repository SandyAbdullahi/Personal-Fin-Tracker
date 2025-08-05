# finance/management/commands/post_recurring.py
from datetime import date

from dateutil.rrule import rrulestr
from django.core.management.base import BaseCommand
from django.db import transaction as db_tx

from finance.models import RecurringTransaction, Transaction


class Command(BaseCommand):
    help = "Create real Transaction rows for every RecurringTransaction due today."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Only show what would be created; do NOT touch the database.",
        )

    # ------------------------------------------------------------------ #
    def handle(self, *args, dry_run=False, **kwargs):  # noqa: D401
        """Find every recurring entry where `next_occurrence ≤ today` and post it."""
        today = date.today()
        due_qs = RecurringTransaction.objects.filter(active=True, next_occurrence__lte=today).select_related(
            "user", "category"
        )

        if not due_qs.exists():
            self.stdout.write(self.style.SUCCESS("Nothing due today."))
            return

        with db_tx.atomic():
            for r in due_qs:
                # loop in case the cadence is < today by more than one step
                while r.active and r.next_occurrence <= today:
                    self._post_single_occurrence(r, dry_run=today if dry_run else None)

            if dry_run:
                db_tx.set_rollback(True)  # never commit in dry-run mode

        self.stdout.write(self.style.SUCCESS(f"✓ Finished. {'(dry-run)' if dry_run else ''}"))

    # ------------------------------------------------------------------ #
    def _post_single_occurrence(self, r: RecurringTransaction, dry_run: bool):
        """Insert a Transaction and push `next_occurrence` forward one step."""
        if not dry_run:
            Transaction.objects.create(
                user=r.user,
                category=r.category,
                amount=r.amount,
                type=r.type,
                description=r.description,
                date=r.next_occurrence,
            )

        # advance to the next date
        rule = rrulestr(r.rrule, dtstart=r.next_occurrence)
        next_date = rule.after(r.next_occurrence)

        # deactivate if finished
        if next_date is None or (r.end_date and next_date > r.end_date):
            r.active = False
        else:
            r.next_occurrence = next_date

        if not dry_run:
            r.save(update_fields=["next_occurrence", "active"])
