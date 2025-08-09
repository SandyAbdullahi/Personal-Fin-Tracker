# finance/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import BudgetViewSet, CategoryViewSet, SavingsGoalViewSet, TransactionViewSet, TransferViewSet, summary
from .views_recurring import RecurringTransactionViewSet, post_due_recurring_transactions

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="categories")
router.register("transactions", TransactionViewSet, basename="transactions")
router.register("goals", SavingsGoalViewSet, basename="goals")
router.register("budgets", BudgetViewSet, basename="budgets")
router.register("transfers", TransferViewSet, basename="transfers")
router.register("recurrings", RecurringTransactionViewSet, basename="recurrings")  # ← add

app_name = "finance"
urlpatterns = [
    path("summary/", summary, name="summary"),  # ← add
    path("post-recurring/", post_due_recurring_transactions, name="post-recurring"),  # ← add
]
urlpatterns += router.urls
