# finance/mixins.py
from django.db import models, transaction
from django.db.models import Max


class PerUserSequenceMixin(models.Model):
    """
    Adds a per-user auto-incrementing local_id.
    Assumes the model has a FK called `user`.
    """

    local_id = models.PositiveIntegerField(editable=False, null=True)

    class Meta:
        abstract = True

    def _next_local_id(self) -> int:
        agg = self.__class__.objects.filter(user=self.user).aggregate(m=Max("local_id"))
        return (agg["m"] or 0) + 1

    def save(self, *args, **kwargs):
        # Only assign on first save (create)
        if self._state.adding and self.local_id is None:
            # Small retry loop in case of race (another row gets the same local_id)
            for _ in range(3):
                try:
                    with transaction.atomic():
                        self.local_id = self._next_local_id()
                        return super().save(*args, **kwargs)
                except Exception:
                    self.local_id = None
        return super().save(*args, **kwargs)
