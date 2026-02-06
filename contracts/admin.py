from django.contrib import admin
from .models import Contract
from django.utils.html import format_html


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "contract_type",
        "old_user",
        "new_user",
        "vehicle",
        "contract_status",
        "end_date",
        "price",
        "is_paid",
        "created_by_owner",
        "created_at",
    )

    list_filter = (
        "contract_type",
        "old_user__user_type",
        "contract_status",
        "new_user__user_type",
        "created_by_owner__user_type",
        ("start_date", admin.DateFieldListFilter),
        ("end_date", admin.DateFieldListFilter),
    )

    search_fields = (
        "old_user__email",
        "new_user__email",
        "old_user__first_name",
        "old_user__last_name",
        "new_user__first_name",
        "new_user__last_name",
        "vehicle__plate_number",
        "vehicle__brand",
        "vehicle__model",
    )

    autocomplete_fields = ("old_user", "new_user", "vehicle")

    readonly_fields = ("created_at", "created_by_owner")

    fieldsets = (
        ("Informations sur le contrat", {
            "fields": (
                "contract_type",
                "old_user",
                "new_user",
                "vehicle",
                "created_by_owner",
            )
        }),
        ("Détails dates", {
            "fields": (
                "start_date",
                "end_date",
            )
        }),
        ("Paiements & Pénalités", {
            "fields": (
                "price",
                "penalty_per_day",
            ),
            "classes": ("collapse",)
        }),
        ("Garantie", {
            "fields": ("warranty_period",),
            "classes": ("collapse",)
        }),
        ("Service", {
            "fields": ("service_type",),
            "classes": ("collapse",)
        }),
        ("Historique", {
            "fields": ("created_at", "updated_at")
        }),
    )

    def save_model(self, request, obj, form, change):
        """
        Assigne automatiquement created_by si le contrat a été créé via l'admin.
        """
        if not obj.created_by_owner:
            obj.created_by_owner = request.user
        super().save_model(request, obj, form, change)