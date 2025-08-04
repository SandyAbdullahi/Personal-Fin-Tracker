# finance/serializers.py
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import Category, SavingsGoal, Transaction


class TransactionSerializer(serializers.ModelSerializer):
    # Accept both names for the incoming integer
    category_id = serializers.IntegerField(write_only=True, required=False)
    category = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Transaction
        fields = (
            "id",
            "category_id",  # write-only alias
            "category",  # write-only (for legacy tests)
            "amount",
            "type",
            "description",
            "date",
        )

    # ------------------------------------------------------------------ #
    # Field-level validation
    # ------------------------------------------------------------------ #
    def _resolve_category(self, value):
        """Return the Category instance or raise 404/400."""
        return get_object_or_404(Category, pk=value)

    def validate_category_id(self, value):
        return self._resolve_category(value)

    def validate_category(self, value):
        return self._resolve_category(value)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value

    # ------------------------------------------------------------------ #
    # Create / update hooks
    # ------------------------------------------------------------------ #
    def create(self, validated_data):
        # Pull whichever alias was provided
        category = validated_data.pop("category", None) or validated_data.pop("category_id", None)
        validated_data["category"] = category

        # Stamp user if request is in context
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["user"] = request.user

        return super().create(validated_data)

    # ------------------------------------------------------------------ #
    # Representation
    # ------------------------------------------------------------------ #
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["category_id"] = instance.category_id  # echo for clients
        rep.pop("category", None)  # keep output tidy
        return rep


# ---------------------------- other serializers ---------------------------- #


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class SavingsGoalSerializer(serializers.ModelSerializer):
    remaining_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True, source="remaining_amount"
    )

    class Meta:
        model = SavingsGoal
        fields = [
            "id",
            "name",
            "target_amount",
            "current_amount",
            "target_date",
            "remaining_amount",
        ]
        read_only_fields = ["id", "remaining_amount"]
