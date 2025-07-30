from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    TransactionViewSet,
    SavingsGoalViewSet,
    summary,
)

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="categories")
router.register(r"transactions", TransactionViewSet, basename="transactions")
router.register(r"goals", SavingsGoalViewSet, basename="goals")

urlpatterns = [
    path("", include(router.urls)),
    path("summary/", summary, name="finance-summary"),
]
