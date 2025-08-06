import django_filters as filters

from .models import Transaction


class TransactionFilter(filters.FilterSet):
    date_from = filters.DateFilter(field_name="date", lookup_expr="gte")
    date_to = filters.DateFilter(field_name="date", lookup_expr="lte")

    class Meta:
        model = Transaction
        fields = {
            "type": ["exact"],
            "category": ["exact"],
        }
