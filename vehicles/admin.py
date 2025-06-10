from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Vehicle, VehicleTransfer

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    # Liste des champs à afficher dans la vue de liste
    list_display = (
        "plate_number",
        "driver_license",
        "serial_number",
        "year",
        "color",
        "brand",
        "model",
        "owner",
        "status",
        "mileage",
        "fuel_type",
        "created_at",
    )

    # Filtres pour la barre latérale
    list_filter = (
        "status",
        "fuel_type",
        "owner",
        "created_at",
    )

    # Champs de recherche
    search_fields = (
        "plate_number",
        "serial_number",
        "brand",
        "model",
    )

    # Champs en lecture seule (non modifiables dans l'admin)
    readonly_fields = (
        "created_at",
        "updated_at",
    )

    # Organisation des champs dans le formulaire d'édition
    fieldsets = (
        (_("Informations générales"), {
            "fields": ("plate_number", "serial_number", "brand", "model", "year", "color")
        }),
        (_("Propriété et statut"), {
            "fields": ("owner", "status", "mileage", "fuel_type")
        }),
        (_("Image"), {
            "fields": ("image",)
        }),
        (_("Historique"), {
            "fields": ("created_at", "updated_at"),
        }),
    )

    # Actions personnalisées
    actions = ["mark_as_available", "mark_as_maintenance"]

    def mark_as_available(self, request, queryset):
        """Marquer les véhicules sélectionnés comme 'Disponible'."""
        updated = queryset.update(status="available")
        self.message_user(request, f"{updated} véhicule(s) marqué(s) comme 'Disponible'.")
    mark_as_available.short_description = _("Marquer comme Disponible")

    def mark_as_maintenance(self, request, queryset):
        """Marquer les véhicules sélectionnés comme 'En maintenance'."""
        updated = queryset.update(status="maintenance")
        self.message_user(request, f"{updated} véhicule(s) marqué(s) comme 'En maintenance'.")
    mark_as_maintenance.short_description = _("Marquer comme En maintenance")


@admin.register(VehicleTransfer)
class VehicleTransferAdmin(admin.ModelAdmin):
    # Liste des champs à afficher dans la vue de liste
    list_display = (
        "vehicle",
        "previous_owner",
        "new_owner",
        "transfer_date",
        "transfer_reason",
    )

    # Filtres pour la barre latérale
    list_filter = (
        "transfer_date",
        "vehicle__brand",
        "vehicle__model",
        "previous_owner",
        "new_owner",
    )

    # Champs de recherche
    search_fields = (
        "vehicle__plate_number",
        "previous_owner__username",
        "new_owner__username",
    )

    # Champs en lecture seule (non modifiables dans l'admin)
    readonly_fields = (
        "transfer_date",
    )

    # Organisation des champs dans le formulaire d'édition
    fieldsets = (
        (_("Détails du transfert"), {
            "fields": ("vehicle", "previous_owner", "new_owner", "transfer_reason")
        }),
        (_("Historique"), {
            "fields": ("transfer_date",),
        }),
    )