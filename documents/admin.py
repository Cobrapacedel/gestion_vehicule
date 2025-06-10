from django.contrib import admin
from .models import DocumentRenewal

@admin.register(DocumentRenewal)
class DocumentRenewalAdmin(admin.ModelAdmin):
    list_display = ("user", "vehicle", "document_type", "amount", "currency", "expiration_date", "paid")
    search_fields = ("user__email", "vehicle__registration")
    list_filter = ("document_type", "paid", "currency", "expiration_date")
    readonly_fields = ("user", "vehicle", "document_type", "amount", "currency", "expiration_date", "payment")

    actions = ["mark_as_paid"]

    def mark_as_paid(self, request, queryset):
        queryset.update(paid=True)
    mark_as_paid.short_description = "Mark as Paid"