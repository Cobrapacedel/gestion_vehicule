from django.contrib import admin
from .models import Recharge, Transaction, Payment, BalanceCurrency, Wallet, FundTransfer

@admin.register(BalanceCurrency)
class BalanceCurrencyAdmin(admin.ModelAdmin):
    list_display = ("balance", "currency")
    search_fields = ("user__email",)
    
@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("address", "network", "public_key")
    search_fields = ("user__email",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "currency", "status", "created_at")
    list_filter = ("currency", "status", "created_at")
    search_fields = ("user__email",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "currency", "method", "created_at", "transaction")
    list_filter = ("currency", "method", "created_at")
    search_fields = ("user__email",)


@admin.register(Recharge)
class RechargeAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "currency", "method", "status", "created_at")
    list_filter = ("currency", "method", "status")
    search_fields = ("user__email",)
    
@admin.register(FundTransfer)
class FundTransferAdmin(admin.ModelAdmin):
    list_display = ("sender", "amount", "currency", "method", "status", "created_at")
    list_filter = ("currency", "method", "status")
    search_fields = ("user__email",)