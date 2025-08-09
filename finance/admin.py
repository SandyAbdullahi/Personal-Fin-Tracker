# finance/admin.py
from django.contrib import admin

from .models import Budget, Category, SavingsGoal, Transaction, Transfer

admin.site.register(Category)
admin.site.register(Transaction)
admin.site.register(SavingsGoal)
admin.site.register(Budget)


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "source_category",
        "destination_category",
        "amount",
        "date",
    )
    search_fields = ("description",)
    list_filter = ("date",)
