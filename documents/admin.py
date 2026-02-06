from django.contrib import admin
from .models import Document, DocumentRenewal


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("document_type", "user", "expiry_date", "is_valid", "created_at")
    list_filter = ("document_type", "is_valid", "created_at")
    search_fields = ("user__email", "document_type")
    date_hierarchy = "created_at"


@admin.register(DocumentRenewal)
class DocumentRenewalAdmin(admin.ModelAdmin):
    list_display = ("document", "vehicle", "old_expiry", "new_expiry", "renewed_at")
    list_filter = ("renewed_at",)
    search_fields = ("document__user__email", "vehicle__plate_number")
    date_hierarchy = "renewed_at"

