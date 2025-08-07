# finance/serializers.py
from dateutil.rrule import rrulestr
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers

from .models import Category, RecurringTransaction, SavingsGoal, Transaction

# ─────────────────────────────── Transactions ────────────────────────────────


class TransactionSerializer(serializers.ModelSerializer):
    # Accept **either** alias when clients post data
    category_id = serializers.IntegerField(write_only=True, required=False)
    category = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Transaction
        fields = (
            "id",
            "category_id",  # write-only alias
            "category",  # write-only (legacy)
            "amount",
            "type",
            "description",
            "date",
        )

    # --------------------------------------------------------------------- #
    # Field-level validation helpers
    # --------------------------------------------------------------------- #
    def _resolve_category(self, value):
        """Return a Category *instance* or raise 404/400."""
        return get_object_or_404(Category, pk=value)

    def validate_category_id(self, value):
        return self._resolve_category(value)

    def validate_category(self, value):
        return self._resolve_category(value)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value

    # --------------------------------------------------------------------- #
    # Create / update hooks
    # --------------------------------------------------------------------- #
    def create(self, validated_data):
        # Pull whichever alias was provided
        category_obj = validated_data.pop("category", None) or validated_data.pop("category_id", None)

        # Always pass the FK **integer** to the ORM
        validated_data["category_id"] = category_obj.pk if hasattr(category_obj, "pk") else category_obj

        # Stamp the user automatically (if request present)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["user"] = request.user

        return super().create(validated_data)

    # --------------------------------------------------------------------- #
    # Representation
    # --------------------------------------------------------------------- #
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["category_id"] = instance.category_id  # echo for clients
        rep.pop("category", None)  # keep output tidy
        return rep


# ─────────────────────────────── Categories ─────────────────────────────────


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


# ───────────────────────────── Savings Goals ────────────────────────────────


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


# ──────────────────────── Recurring Transactions ────────────────────────────


class RecurringTransactionSerializer(serializers.ModelSerializer):
    """
    Accepts **either** `category_id` or `category`.
    DRF will still render the FK back as an integer `category_id`.
    """

    category_id = serializers.IntegerField(write_only=True, required=False)
    category = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = RecurringTransaction
        fields = [
            "id",
            "category_id",  # write-only alias
            "category",  # write-only (legacy)
            "amount",
            "type",
            "description",
            "rrule",
            "next_occurrence",
            "end_date",
            "active",
        ]
        read_only_fields = ["id", "active"]

    # ───────────── field-level validation ───────────── #
    def _resolve_category(self, value):
        return get_object_or_404(Category, pk=value)

    def validate_category_id(self, value):
        return self._resolve_category(value)

    def validate_category(self, value):
        return self._resolve_category(value)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value

    def validate_rrule(self, value):
        try:
            rrulestr(value, dtstart=timezone.now())
        except Exception as exc:
            raise serializers.ValidationError("Invalid RRULE string.") from exc
        return value

    # ───────────── create hook ───────────── #
    def create(self, validated):
        # pick whichever alias was supplied
        cat_obj = validated.pop("category", None) or validated.pop("category_id", None)
        validated["category_id"] = cat_obj.pk if hasattr(cat_obj, "pk") else cat_obj

        validated["user"] = self.context["request"].user
        return super().create(validated)

    # ───────────── representation ───────────── #
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["category_id"] = instance.category_id
        rep.pop("category", None)
        return rep
