# finance/serializers.py


from dateutil.rrule import rrulestr
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import Category, RecurringTransaction, SavingsGoal, Transaction


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
    remaining_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

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


# ──────────────────────────  RecurringTransaction  ────────────────────────── #


class RecurringTransactionSerializer(serializers.ModelSerializer):
    """
    Accepts either `category` **or** `category_id` (int PK) in the payload.
    """

    # --- allow both aliases ------------------------------------------------ #
    category = serializers.IntegerField(write_only=True, required=False)
    category_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = RecurringTransaction
        fields = [
            "id",
            "category",  # write-only
            "category_id",  # write-only alias
            "amount",
            "type",
            "description",
            "rrule",
            "next_occurrence",
            "end_date",
            "active",
        ]
        read_only_fields = ["id", "active"]

    # ---- basic validations ------------------------------------------------ #
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value

    def validate_rrule(self, value):
        try:
            rrulestr(value)  # will raise if invalid
        except Exception:
            raise serializers.ValidationError("Invalid RRULE string.")
        return value

    # ---- normalise the category field  ----------------------------------- #
    def _get_category(self, data):
        from django.shortcuts import get_object_or_404

        raw = data.pop("category", None) or data.pop("category_id", None)
        return get_object_or_404(Category, pk=raw)

    # ---- create / update -------------------------------------------------- #
    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        validated_data["category"] = self._get_category(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "category" in validated_data or "category_id" in validated_data:
            validated_data["category"] = self._get_category(validated_data)
        return super().update(instance, validated_data)

    # ---- representation --------------------------------------------------- #
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["category_id"] = instance.category_id  # echo for clients
        rep.pop("category", None)  # keep output tidy
        return rep
