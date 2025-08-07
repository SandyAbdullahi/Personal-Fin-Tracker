# finance/admin.py
from django.contrib import admin

from .models import Budget, Category, SavingsGoal, Transaction

admin.site.register(Category)
admin.site.register(Transaction)
admin.site.register(SavingsGoal)
admin.site.register(Budget)
