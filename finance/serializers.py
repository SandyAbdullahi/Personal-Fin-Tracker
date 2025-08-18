# finance/serializers.py
"""
All serializers for the **finance** app.

Sections
────────
1.  Transactions & Categories
2.  Savings-Goals
3.  Recurring Transactions
4.  Budgets / Envelopes
5.  Debts & Payments
6.  Category-to-Category Transfers
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict

from dateutil.rrule import rrulestr
from django.core.exceptions import FieldDoesNotExist
from django.db import transaction as db_tx
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers

from .models import Budget, Category, Debt, Payment, RecurringTransaction, SavingsGoal, Transaction, Transfer

# ─────────────────────────────── 1. Transactions ──────────────────────────────


class TransactionSerializer(serializers.ModelSerializer):
    # allow either alias when POSTing
    category_id = serializers.IntegerField(write_only=True, required=False)
    category = serializers.IntegerField(write_only=True, required=False)

    # expose the FK to the originating transfer (read-only)
    transfer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Transaction
        fields = (
            "id",
            "category_id",  # incoming alias
            "category",  # legacy alias
            "amount",
            "type",
            "description",
            "date",
            "transfer",
        )
        read_only_fields = ["id", "transfer"]

    # ───────── helpers ───────── #
    def _current_user(self):
        req = self.context.get("request")
        return getattr(req, "user", None) if req else None

    def _resolve_category(self, value):
        """
        Resolve by PK or instance. If a user is present in context,
        ensure the category belongs to them.
        """
        cat = value if isinstance(value, Category) else Category.objects.filter(pk=value).first()
        if not cat:
            raise serializers.ValidationError("Invalid category.")

        user = self._current_user()
        if user and cat.user_id != user.id:
            raise serializers.ValidationError("Invalid category.")
        return cat

    def validate_category_id(self, value):
        return self._resolve_category(value)

    def validate_category(self, value):
        return self._resolve_category(value)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value

    # create
    def create(self, validated: Dict[str, Any]):
        cat = validated.pop("category", None) or validated.pop("category_id", None)
        validated["category_id"] = cat.pk if hasattr(cat, "pk") else cat

        request = self.context.get("request")
        if request and getattr(request, "user", None) and request.user.is_authenticated:
            validated["user"] = request.user
        return super().create(validated)

    # update (supports category/category_id)
    def update(self, instance, validated_data):
        cat_obj = validated_data.pop("category", None) or validated_data.pop("category_id", None)
        if cat_obj is not None:
            instance.category_id = cat_obj.pk if hasattr(cat_obj, "pk") else cat_obj

        for field in ("amount", "type", "description", "date"):
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        request = self.context.get("request")
        if request and getattr(request.user, "is_authenticated", False):
            instance.user = request.user

        instance.save()
        return instance

    def to_representation(self, instance: Transaction):
        rep = super().to_representation(instance)
        rep["category_id"] = instance.category_id
        rep.pop("category", None)
        return rep


# ──────────────────────────────── Category ────────────────────────────


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]

    def validate_name(self, value: str):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("This field may not be blank.")

        # Enforce per-user uniqueness (case-insensitive)
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            qs = Category.objects.filter(user=user, name__iexact=value)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError("You already have a category with this name.")
        return value


# ──────────────────────────────── 2. Savings Goals ────────────────────────────


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


# ───────────────────────────── 3. Recurring Transactions ───────────────────────


class RecurringTransactionSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True, required=False)
    category = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = RecurringTransaction
        fields = [
            "id",
            "category_id",
            "category",
            "amount",
            "type",
            "description",
            "rrule",
            "next_occurrence",
            "end_date",
            "active",
        ]
        read_only_fields = ["id", "active"]

    def _current_user(self):
        req = self.context.get("request")
        return getattr(req, "user", None) if req else None

    def _resolve_category(self, value: int) -> Category:
        user = self._current_user()
        return get_object_or_404(Category, pk=value, user=user)

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
        except Exception as exc:  # noqa: BLE001
            raise serializers.ValidationError("Invalid RRULE string.") from exc
        return value

    def create(self, validated):
        cat = validated.pop("category", None) or validated.pop("category_id", None)
        validated["category_id"] = cat.pk if hasattr(cat, "pk") else cat
        validated["user"] = self.context["request"].user
        return super().create(validated)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["category_id"] = instance.category_id
        rep.pop("category", None)
        return rep


# ───────────────────────────────── 4. Budgets ─────────────────────────────────


class BudgetSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    # expose the annotated "spent" as amount_spent
    amount_spent = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True, source="spent")
    remaining = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    percent_used = serializers.FloatField(read_only=True)
    net_transfer = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    effective_limit = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Budget
        fields = [
            "id",
            "category",
            "limit",
            "period",
            "amount_spent",  # from "spent" annotation
            "net_transfer",  # +in −out
            "effective_limit",
            "remaining",
            "percent_used",
        ]
        read_only_fields = [
            "id",
            "amount_spent",
            "net_transfer",
            "effective_limit",
            "remaining",
            "percent_used",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Restrict category choices to the current user
        req = self.context.get("request")
        user = req.user if req and getattr(req, "user", None) else self.context.get("request_user")
        self.fields["category"].queryset = Category.objects.filter(user=user) if user else Category.objects.none()

    def validate_category(self, value):
        req = self.context.get("request")
        user = req.user if req and getattr(req, "user", None) else self.context.get("request_user")
        if not user or value.user_id != getattr(user, "id", None):
            raise serializers.ValidationError("Category does not belong to the authenticated user.")
        return value

    def validate_limit(self, value):
        if value <= 0:
            raise serializers.ValidationError("Limit must be positive.")
        return value

    def create(self, validated):
        req = self.context.get("request")
        validated["user"] = req.user if req else self.context["request_user"]
        return super().create(validated)

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        def fmt(value) -> str:
            d = Decimal(value or "0")
            return f"{d.quantize(Decimal('0.00'))}"

        # amount_spent can come from annotation `spent` or the property
        spent_val = getattr(instance, "spent", None)
        if spent_val is None:
            spent_val = getattr(instance, "amount_spent", None)
        rep["amount_spent"] = fmt(spent_val)

        # remaining may be annotated or computed property
        remaining_val = getattr(instance, "remaining", None)
        if remaining_val is None:
            amt = getattr(instance, "amount_spent", None)
            if amt is None:
                amt = spent_val
            remaining_val = Decimal(instance.limit) - Decimal(amt or 0)
        rep["remaining"] = fmt(remaining_val)

        return rep


# ──────────────────────────────── 5. Debts & Payments ─────────────────────────


class DebtSerializer(serializers.ModelSerializer):
    balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Debt
        fields = [
            "id",
            "name",
            "principal",
            "interest_rate",
            "minimum_payment",
            "opened_date",
            "category",
            "balance",
        ]
        read_only_fields = ["id", "balance"]

    def validate_principal(self, value):
        if value <= 0:
            raise serializers.ValidationError("Principal must be positive.")
        return value

    def validate_interest_rate(self, value):
        if value < 0:
            raise serializers.ValidationError("Interest rate cannot be negative.")
        return value

    def validate_minimum_payment(self, value):
        if value < 0:
            raise serializers.ValidationError("Minimum payment cannot be negative.")
        return value

    def create(self, validated):
        validated["user"] = self.context["request"].user
        return super().create(validated)


class PaymentSerializer(serializers.ModelSerializer):
    # Optional memo supported by the model (blank allowed)
    memo = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Payment
        fields = ["id", "debt", "amount", "date", "memo"]
        read_only_fields = ["id"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value

    def create(self, validated):
        request_user = self.context["request"].user

        # Ensure the debt exists and belongs to the user
        debt_value = validated["debt"]
        debt_pk = getattr(debt_value, "pk", debt_value)
        debt = get_object_or_404(Debt, pk=debt_pk, user=request_user)

        with db_tx.atomic():
            validated["debt"] = debt
            validated["user"] = request_user
            payment = super().create(validated)

            # If Debt has a *real* balance column, update it; otherwise skip.
            try:
                Debt._meta.get_field("balance")  # raises if not a concrete field
            except FieldDoesNotExist:
                pass
            else:
                Debt.objects.filter(pk=debt.pk).update(balance=F("balance") - payment.amount)

        return payment


# ───────────────────────────── 6. Category-to-Category Transfer ───────────────


class TransferSerializer(serializers.ModelSerializer):
    # Restrict both sides to the current user's categories
    source_category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.none())
    destination_category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.none())
    # make description optional and allow blank strings (model has blank=True)
    description = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = Transfer
        fields = [
            "id",
            "source_category",
            "destination_category",
            "amount",
            "date",
            "description",
        ]
        read_only_fields = ["id"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        req = self.context.get("request")
        user = getattr(req, "user", None) if req else None
        qs = Category.objects.filter(user=user) if user else Category.objects.none()
        self.fields["source_category"].queryset = qs
        self.fields["destination_category"].queryset = qs

    def validate_amount(self, value: Decimal) -> Decimal:
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value

    def validate(self, attrs):
        """
        Support PATCH: if a side isn't in attrs, pull it from the instance.
        Only error if both are known and equal.
        """
        instance = getattr(self, "instance", None)
        src = attrs.get("source_category") or (instance.source_category if instance else None)
        dst = attrs.get("destination_category") or (instance.destination_category if instance else None)
        if src and dst and src == dst:
            raise serializers.ValidationError("Source and destination must be different.")
        return attrs

    def create(self, validated: Dict[str, Any]) -> Transfer:
        user = self.context["request"].user
        src_cat: Category = validated["source_category"]
        dst_cat: Category = validated["destination_category"]
        amount: Decimal = validated["amount"]
        date = validated["date"]
        desc = validated.get("description", "")

        with db_tx.atomic():
            transfer = Transfer.objects.create(
                user=user,
                source_category=src_cat,
                destination_category=dst_cat,
                amount=amount,
                date=date,
                description=desc,
            )
            # Create mirror pair
            Transaction.objects.bulk_create(
                [
                    Transaction(
                        user=user,
                        category=src_cat,
                        amount=amount,
                        type="EX",
                        description=desc,
                        date=date,
                        transfer=transfer,
                    ),
                    Transaction(
                        user=user,
                        category=dst_cat,
                        amount=amount,
                        type="IN",
                        description=desc,
                        date=date,
                        transfer=transfer,
                    ),
                ]
            )
        return transfer

    def update(self, instance: Transfer, validated: Dict[str, Any]) -> Transfer:
        """
        Sync the two linked transactions on any change.
        Heal if one is missing; prune extras if present.
        """
        src = validated.get("source_category", instance.source_category)
        dst = validated.get("destination_category", instance.destination_category)
        amount = validated.get("amount", instance.amount)
        date = validated.get("date", instance.date)
        desc = validated.get("description", instance.description)

        with db_tx.atomic():
            # Update the transfer row itself
            instance.source_category = src
            instance.destination_category = dst
            instance.amount = amount
            instance.date = date
            instance.description = desc
            instance.save()

            # Fetch existing linked transactions
            txs = list(instance.transactions.all())

            def upsert(kind: str, category: Category) -> Transaction:
                for tx in txs:
                    if tx.type == kind:
                        tx.category = category
                        tx.amount = amount
                        tx.date = date
                        tx.description = desc
                        tx.user = instance.user
                        tx.save()
                        return tx
                return Transaction.objects.create(
                    user=instance.user,
                    category=category,
                    amount=amount,
                    type=kind,
                    description=desc,
                    date=date,
                    transfer=instance,
                )

            tx_out = upsert("EX", src)
            tx_in = upsert("IN", dst)

            # Remove any extras
            instance.transactions.exclude(pk__in=[tx_out.pk, tx_in.pk]).delete()

        return instance

    def to_representation(self, instance: Transfer):
        rep = super().to_representation(instance)
        rep["transactions"] = [tx.id for tx in instance.transactions.order_by("id")]
        return rep
