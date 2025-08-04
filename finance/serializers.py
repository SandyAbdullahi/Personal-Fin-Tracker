from rest_framework import serializers
from .models import Transaction, Category, SavingsGoal


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")  # user is implicit

    def create(self, validated_data):
        return Category.objects.create(
            user=self.context["request"].user, **validated_data
        )


class TransactionSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )

    class Meta:
        model = Transaction
        fields = ("id", "category", "amount", "date", "type", "description")
        read_only_fields = ["user"]


class SavingsGoalSerializer(serializers.ModelSerializer):
    amount_saved = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = SavingsGoal
        fields = [
            "id",
            "name",
            "target_amount",
            "deadline",
            "amount_saved",
            "created_at",
        ]
        read_only_fields = ["created_at"]
