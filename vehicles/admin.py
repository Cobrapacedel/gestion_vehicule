from django.contrib import admin
from .models import (
    Vehicle, VehicleStatusHistory
)
# ============================
#  VEHICLE
# ============================
@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("plate_number", "brand", "model", "year", "owner", "status","fuel_type",  "mileage")
    list_filter = ("status", "vehicle_type", "fuel_type", "year")
    search_fields = ("plate_number", "brand", "model", "serial_number", "owner__email")
    ordering = ("-year",)
    readonly_fields = ("created_at", "updated_at")
   # inlines = [VehicleBoughtInline, VehicleSoldInline]

# ============================
#  HISTORIQUE DES STATUTS
# ============================
@admin.register(VehicleStatusHistory)
class VehicleStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("vehicle", "old_status", "new_status", "changed_by", "changed_at")
    list_filter = ("new_status", "old_status")
    search_fields = ("vehicle__plate_number", "changed_by__email")
    ordering = ("-changed_at",)