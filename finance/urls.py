# finance/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BudgetViewSet, CategoryViewSet, SavingsGoalViewSet, TransactionViewSet, TransferViewSet, summary
from .views_debt import DebtViewSet, PaymentViewSet
from .views_recurring import RecurringTransactionViewSet, post_due_recurring_transactions

app_name = "finance"

router = DefaultRouter()
router.register(r"transactions", TransactionViewSet, basename="transactions")  # 👈 plural
router.register(r"categories", CategoryViewSet, basename="categories")  # 👈 plural
router.register(r"goals", SavingsGoalViewSet, basename="goals")  # 👈 plural
router.register(r"recurrings", RecurringTransactionViewSet, basename="recurrings")
router.register(r"budgets", BudgetViewSet, basename="budgets")
router.register(r"debts", DebtViewSet, basename="debts")
router.register(r"payments", PaymentViewSet, basename="payments")
router.register(r"transfers", TransferViewSet, basename="transfer")

urlpatterns = [
    path("summary/", summary, name="summary"),
    path("post-recurring/", post_due_recurring_transactions, name="post-recurring"),
    path("", include(router.urls)),
]
