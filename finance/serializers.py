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

    # field-level validation
    def _resolve_category(self, value: int) -> Category:
        return get_object_or_404(Category, pk=value)

    def validate_category_id(self, value):
        return self._resolve_category(value)

    def validate_category(self, value):
        return self._resolve_category(value)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value

    # create hook
    def create(self, validated: Dict[str, Any]):
        cat = validated.pop("category", None) or validated.pop("category_id", None)
        validated["category_id"] = cat.pk if hasattr(cat, "pk") else cat

        request = self.context.get("request")
        if request and getattr(request, "user", None) and request.user.is_authenticated:
            validated["user"] = request.user
        return super().create(validated)

    def to_representation(self, instance: Transaction):
        rep = super().to_representation(instance)
        rep["category_id"] = instance.category_id
        rep.pop("category", None)
        return rep


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


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

    amount_spent = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    remaining = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    percent_used = serializers.FloatField(read_only=True)

    class Meta:
        model = Budget
        fields = [
            "id",
            "category",
            "limit",
            "period",
            "amount_spent",
            "remaining",
            "percent_used",
        ]
        read_only_fields = ["id", "amount_spent", "remaining", "percent_used"]

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
        # Fallback to model properties if annotations weren't present
        if rep.get("amount_spent") is None:
            rep["amount_spent"] = f"{instance.amount_spent:.2f}"
        if rep.get("remaining") is None:
            rep["remaining"] = f"{instance.remaining:.2f}"
        if rep.get("percent_used") is None:
            rep["percent_used"] = float(instance.percent_used)
        return rep


# ──────────────────────────────── 5. Debts & Payments ─────────────────────────


class DebtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debt
        fields = [
            "id",
            "name",
            "principal",
            "balance",
            "interest_rate",
        ]
        read_only_fields = ["id", "balance"]

    def validate_principal(self, value):
        if value <= 0:
            raise serializers.ValidationError("Principal must be positive.")
        return value

    def create(self, validated):
        validated["user"] = self.context["request"].user
        return super().create(validated)


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "debt", "amount", "date"]
        read_only_fields = ["id"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value

    def create(self, validated):
        request_user = self.context["request"].user
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
    source_category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    destination_category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

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

    # amount-level validation (attaches error to "amount")
    def validate_amount(self, value: Decimal) -> Decimal:
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value

    # cross-field validation — works for partial updates, too
    def validate(self, attrs):
        src = attrs.get("source_category")
        dst = attrs.get("destination_category")

        if self.instance:
            if src is None:
                src = self.instance.source_category
            if dst is None:
                dst = self.instance.destination_category

        if src is not None and dst is not None and src == dst:
            raise serializers.ValidationError("Source and destination must be different.")
        return attrs

    def create(self, validated):
        user = self.context["request"].user
        src: Category = validated["source_category"]
        dst: Category = validated["destination_category"]
        amount: Decimal = validated["amount"]
        date = validated["date"]
        desc = validated.get("description") or ""  # avoid NULL in CharField

        with db_tx.atomic():
            transfer = Transfer.objects.create(
                user=user,
                source_category=src,
                destination_category=dst,
                amount=amount,
                date=date,
                description=desc,
            )
            # mirror as EX (out) and IN (in)
            Transaction.objects.bulk_create(
                [
                    Transaction(
                        user=user,
                        category=src,
                        amount=amount,
                        type="EX",
                        description=desc,
                        date=date,
                        transfer=transfer,
                    ),
                    Transaction(
                        user=user,
                        category=dst,
                        amount=amount,
                        type="IN",
                        description=desc,
                        date=date,
                        transfer=transfer,
                    ),
                ]
            )
        return transfer

    def update(self, instance: Transfer, validated):
        """
        Keep the two mirrored transactions in sync with updates to the Transfer.
        Also 'heal' the pair if one side is missing.
        """
        # normalize description (CharField is NOT NULL)
        if "description" in validated and validated["description"] is None:
            validated["description"] = ""

        # apply incoming changes to the transfer
        for field in (
            "source_category",
            "destination_category",
            "amount",
            "date",
            "description",
        ):
            if field in validated:
                setattr(instance, field, validated[field])
        instance.save()

        user = instance.user
        src = instance.source_category
        dst = instance.destination_category
        amt = instance.amount
        date = instance.date
        desc = instance.description or ""

        with db_tx.atomic():
            # load existing linked transactions
            existing = {t.type: t for t in instance.transactions.all()}

            # create missing sides if necessary
            if "EX" not in existing:
                existing["EX"] = Transaction.objects.create(
                    user=user,
                    category=src,
                    amount=amt,
                    type="EX",
                    description=desc,
                    date=date,
                    transfer=instance,
                )
            if "IN" not in existing:
                existing["IN"] = Transaction.objects.create(
                    user=user,
                    category=dst,
                    amount=amt,
                    type="IN",
                    description=desc,
                    date=date,
                    transfer=instance,
                )

            # update common fields on both
            Transaction.objects.filter(pk__in=[existing["EX"].pk, existing["IN"].pk]).update(
                amount=amt, date=date, description=desc
            )

            # ensure categories are on the correct sides
            if existing["EX"].category_id != src.id:
                existing["EX"].category = src
                existing["EX"].save(update_fields=["category"])
            if existing["IN"].category_id != dst.id:
                existing["IN"].category = dst
                existing["IN"].save(update_fields=["category"])

        return instance

    def to_representation(self, instance: Transfer):
        rep = super().to_representation(instance)
        rep["transactions"] = [tx.id for tx in instance.transactions.order_by("id")]
        return rep
