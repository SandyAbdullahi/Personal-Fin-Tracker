# finance/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    TransactionViewSet,
    SavingsGoalViewSet,
    summary,
)

app_name = "finance"

router = DefaultRouter()

# ⬇️  keep the URL path plural, but use a *singular* basename
router.register(r"transactions", TransactionViewSet, basename="transaction")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"goals", SavingsGoalViewSet, basename="goal")

urlpatterns = [
    path("summary/", summary, name="summary"),
    path("", include(router.urls)),
]
