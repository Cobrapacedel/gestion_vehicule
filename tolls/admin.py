from django.contrib import admin
from .models import Toll, TollBooth, TollPayment, TollTransaction


@admin.register(Toll)
class TollAdmin(admin.ModelAdmin):
    list_display = ('name', 'highway_name', 'region')
    search_fields = ('name', 'highway_name', 'region')


@admin.register(TollBooth)
class TollBoothAdmin(admin.ModelAdmin):
    list_display = ('toll', 'booth_number', 'location')
    search_fields = ('toll__name', 'booth_number', 'location')
    list_filter = ('toll',)


@admin.register(TollPayment)
class TollPaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'toll_booth', 'amount', 'currency', 'payment_method', 'status', 'created_at')
    search_fields = ('user__username', 'toll_booth__booth_number')
    list_filter = ('status', 'currency', 'payment_method', 'created_at')


@admin.register(TollTransaction)
class TollTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'payment', 'status', 'confirmed_at')
    search_fields = ('transaction_id', 'payment__user__username')
    list_filter = ('status', 'confirmed_at')