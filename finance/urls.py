# finance/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, TransactionViewSet, SavingsGoalViewSet, summary

app_name = "finance"

router = DefaultRouter()
router.register(r"transactions", TransactionViewSet, basename="transactions")  # 👈 plural
router.register(r"categories",   CategoryViewSet,    basename="categories")    # 👈 plural
router.register(r"goals",        SavingsGoalViewSet, basename="goals")         # 👈 plural

urlpatterns = [
    path("summary/", summary, name="summary"),
    path("", include(router.urls)),
]
