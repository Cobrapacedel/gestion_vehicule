from django.contrib import admin
from .models import Toll, TollBooth, TollDetection, TollDebt

@admin.register(Toll)
class TollAdmin(admin.ModelAdmin):
    list_display = ('name', 'highway_name', 'region', 'amount', 'currency')
    search_fields = ('name', 'highway_name', 'region')
    ordering = ('name',)


@admin.register(TollBooth)
class TollBoothAdmin(admin.ModelAdmin):
    list_display = ('toll', 'booth_number', 'passage_date', 'owner', 'driver')
    search_fields = ('toll__name', 'booth_number', 'vehicle__plate_number', 'driver__email')
    list_filter = ('toll',)

    # Méthodes pour afficher le propriétaire et le chauffeur
    def owner(self, obj):
        return getattr(obj.vehicle, 'owner', None)
    owner.admin_order_field = 'vehicle__owner'
    owner.short_description = 'Propriétaire du véhicule'

    def driver(self, obj):
        return getattr(obj.vehicle, 'driver', None)
    driver.admin_order_field = 'vehicle__driver'
    driver.short_description = 'Chauffeur'

@admin.register(TollDetection)
class TollDetectionAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'booth', 'detected_at', 'processed')
    search_fields = ('vehicle', 'booth__booth_number', 'booth__toll__name')
    list_filter = ('processed',)


@admin.register(TollDebt)
class TollDebtAdmin(admin.ModelAdmin):
    list_display = ('driver', 'amount_due', 'is_fully_paid', 'interest_rate', 'created_at', 'updated_at')
    search_fields = ('driver__email',)
    list_filter = ('is_fully_paid', 'interest_rate')
