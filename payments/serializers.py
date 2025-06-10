from rest_framework import serializers
from .models import Recharge, Transaction, Payment, Balance

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"
        read_only_fields = ["user", "date", "transaction_id", "reference", "status"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ["user", "payment_date", "transaction"]


class RechargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recharge
        fields = "__all__"
        read_only_fields = ["user", "status", "requested_at", "completed_at", "transaction"]


class BalanceSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()

    class Meta:
        model = Balance
        fields = ["htg_balance", "usd_balance", "btg_balance", "btc_balance", "usdt_balance", "total"]

    def get_total(self, obj):
        return obj.total_balance()