# finance/pagination.py
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """Global default for every DRF list endpoint."""

    page_size = 20  # ← one page = 20 objects
    page_size_query_param = "page_size"  # allow ?page_size=XXX overrides
    max_page_size = 100  # upper-bound the override
