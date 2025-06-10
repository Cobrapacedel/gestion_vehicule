from django.contrib import admin
from .models import Recharge, Transaction, Payment, Balance

@admin.register(Balance)
class BalanceAdmin(admin.ModelAdmin):
    list_display = ("user", "htg_balance", "usd_balance", "btc_balance", "btg_balance", "usdt_balance")
    search_fields = ("user__email",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "currency", "status", "date", "reference")
    list_filter = ("currency", "status", "date")
    search_fields = ("user__email", "reference")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "currency", "payment_type", "payment_date", "transaction")
    list_filter = ("currency", "payment_type", "payment_date")
    search_fields = ("user__email",)


@admin.register(Recharge)
class RechargeAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "currency", "method", "status", "requested_at", "completed_at")
    list_filter = ("currency", "method", "status")
    search_fields = ("user__email",)