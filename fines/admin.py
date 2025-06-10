# admin.py
from django.contrib import admin
from .models import Violation, Fine, FinePay, DeletedFine

@admin.register(Violation)
class ViolationAdmin(admin.ModelAdmin):
    list_display = ("reason", "amount", "currency")
    search_fields = ("reason",)

@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ("fine_id", "user", "vehicle", "violation", "base_amount", "is_paid", "due_date")
    list_filter = ("is_paid", "currency", "violation_date")
    search_fields = ("fine_id", "user__email", "vehicle__plate_number")

@admin.register(FinePay)
class FinePayAdmin(admin.ModelAdmin):
    list_display = ("fine", "user", "amount", "currency", "paid", "payment_date")
    list_filter = ("paid", "currency")
    search_fields = ("fine__fine_id", "user__email")

@admin.register(DeletedFine)
class DeletedFineAdmin(admin.ModelAdmin):
    list_display = ("original_id", "user", "amount", "deleted_by", "deleted_at")
    search_fields = ("original_id", "user__email", "deleted_by__email")
