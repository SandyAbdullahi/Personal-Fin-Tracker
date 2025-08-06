# finance/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, SavingsGoalViewSet, TransactionViewSet, summary
from .views_recurring import post_due_recurring_transactions

app_name = "finance"

router = DefaultRouter()
router.register(r"transactions", TransactionViewSet, basename="transactions")  # 👈 plural
router.register(r"categories", CategoryViewSet, basename="categories")  # 👈 plural
router.register(r"goals", SavingsGoalViewSet, basename="goals")  # 👈 plural

urlpatterns = [
    path("summary/", summary, name="summary"),
    path("post-recurring/", post_due_recurring_transactions, name="post-recurring"),
    path("", include(router.urls)),
]
