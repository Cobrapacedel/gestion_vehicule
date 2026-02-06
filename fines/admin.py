from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import Sum
from .models import Violation, Fine, DeletedFine
from vehicles.models import Vehicle
from .forms import FineForm, DeletedFineForm

# ---------------- Utilitaires ----------------
def make_badge(user_obj, badge_class="badge-owner", fallback="N/A"):
    if user_obj:
        try:
            url = reverse("admin:users_customuser_change", args=[user_obj.id])
            return format_html('<a href="{}" class="admin-badge {}">{}</a>', url, badge_class, user_obj.email)
        except Exception:
            return fallback
    return fallback

def make_vehicle_card(vehicle):
    if vehicle:
        url = reverse(f"admin:{vehicle._meta.app_label}_{vehicle._meta.model_name}_change", args=[vehicle.id])
        return format_html(
            '<div class="vehicle-card">'
            '<strong>Marque:</strong> {}<br>'
            '<strong>Modèle:</strong> {}<br>'
            '<strong>Plaque:</strong> {}<br>'
            '<strong>Couleur:</strong> {}'
            '</div>',
            vehicle.brand,
            vehicle.model,
            format_html('<a href="{}">{}</a>', url, vehicle.plate_number),
            vehicle.color
        )
    return "N/A"

# -------------------- FineAdmin --------------------
@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    form = FineForm

    list_display = (
        "fine_id",
        "owner_badge",
        "driver_license_field",
        "issuer_badge",
        "vehicle_info_field",
        "violation_reason_display",
        "violation_amount_display",
        "is_paid_colored",
        "due_date_display",
    )
    search_fields = ("fine_id", "owner__email", "driver__email", "vehicle__plate_number")
    list_filter = ("is_paid", "violation", "vehicle")
    date_hierarchy = "issued_at"

    fieldsets = (
        (None, {"fields": ("driver", "plate_number", "vin_number", "issuer", "violation", "reason")}),
        ("Infos système", {"classes": ("collapse",), "fields": ("fine_id", "violation_date", "issued_at")}),
    )

    class Media:
        css = {'all': ('admin_custom.css',)}

    def get_readonly_fields(self, request, obj=None):
        readonly = ["violation_date", "issued_at", "fine_id"]
        if obj:
            readonly += ["driver_license_field", "vehicle_info_field", "owner_badge"]
        return readonly

    # ---------------- Dashboard ----------------
    def changelist_view(self, request, extra_context=None):
        qs = self.get_queryset(request)
        total_amount = qs.aggregate(total=Sum('violation__amount'))['total'] or 0
        total_paid = qs.filter(is_paid=True).aggregate(total=Sum('violation__amount'))['total'] or 0
        total_remaining = total_amount - total_paid
        paid_count = qs.filter(is_paid=True).count()
        unpaid_count = qs.filter(is_paid=False).count()

        extra_context = extra_context or {}
        extra_context['fine_stats'] = format_html(
            '<div class="dashboard-box">'
            'Total Contraventions: {} &nbsp; '
            '<span class="status-paid">Payé: {}</span> &nbsp; '
            '<span class="status-unpaid">Reste: {}</span> &nbsp; '
            '<span class="status-paid">Payées: {}</span> &nbsp; '
            '<span class="status-unpaid">Non payées: {}</span>'
            '</div>',
            total_amount, total_paid, total_remaining, paid_count, unpaid_count
        )
        return super().changelist_view(request, extra_context=extra_context)

    # ---------------- Champs ----------------
    def owner_badge(self, obj):
        vehicle = getattr(obj, "vehicle", None)
        owner = getattr(vehicle, "owner", None) if vehicle else getattr(obj, "owner", None)
        return make_badge(owner)
    owner_badge.short_description = "Propriétaire"

    def issuer_badge(self, obj):
        return make_badge(getattr(obj, "issuer", None), badge_class="badge-staff")
    issuer_badge.short_description = "Staff"

    def driver_license_field(self, obj):
        driver = getattr(obj, "driver", None)
        return driver.driver_license if driver and driver.driver_license else "Pas de permis"
    driver_license_field.short_description = "Permis"

    def vehicle_info_field(self, obj):
        vehicle = getattr(obj, "vehicle", None)
        return make_vehicle_card(vehicle)
    vehicle_info_field.short_description = "Véhicule"

    def violation_reason_display(self, obj):
        violation = getattr(obj, "violation", None)
        return violation.reason if violation else "Pas de violation"
    violation_reason_display.short_description = "Raison"

    def violation_amount_display(self, obj):
        violation = getattr(obj, "violation", None)
        return format_html('<strong>{} {}</strong>', violation.amount, violation.currency) if violation else "-"
    violation_amount_display.short_description = "Montant"

    def is_paid_colored(self, obj):
        return format_html('<span class="status-paid">✅</span>' if obj.is_paid else '<span class="status-unpaid">❌</span>')
    is_paid_colored.short_description = "Payé"

    def due_date_display(self, obj):
        return format_html('<span class="due-date-icon">⏰ {}</span>', obj.due_date.strftime('%d/%m/%Y')) if getattr(obj, 'due_date', None) else "-"
    due_date_display.short_description = "Dat limit"

    # ---------------- Save automatique ----------------
    def save_model(self, request, obj, form, change):
        if obj.driver:
            obj.driver_license = obj.driver.driver_license

        vehicle = None
        if getattr(obj, "plate_number", None):
            vehicle = Vehicle.objects.filter(plate_number=obj.plate_number).first()
        elif getattr(obj, "serial_number", None):
            vehicle = Vehicle.objects.filter(serial_number=obj.serial_number).first()
        obj.vehicle = vehicle

        if not obj.issuer:
            obj.issuer = request.user
        super().save_model(request, obj, form, change)

# -------------------- DeletedFineAdmin --------------------
@admin.register(DeletedFine)
class DeletedFineAdmin(admin.ModelAdmin):
    form = DeletedFineForm
    list_display = ("original_id", "owner_badge", "amount_display", "deleted_by_badge", "delete_reason_display", "deleted_at")
    search_fields = ("original_id", "owner__email", "deleted_by__email", "delete_reason")
    list_filter = ("deleted_at",)
    date_hierarchy = "deleted_at"

    class Media:
        css = {'all': ('admin_custom.css',)}

    def owner_badge(self, obj):
        return make_badge(obj.owner)
    owner_badge.short_description = "Propriétaire"

    def deleted_by_badge(self, obj):
        return make_badge(obj.deleted_by, badge_class="badge-staff")
    deleted_by_badge.short_description = "Supprimé par"

    def amount_display(self, obj):
        return format_html('<strong>{}</strong>', obj.amount)
    amount_display.short_description = "Montant"

    def delete_reason_display(self, obj):
        return obj.delete_reason or "-"
    delete_reason_display.short_description = "Raison"


# -------------------- ViolationAdmin --------------------
@admin.register(Violation)
class ViolationAdmin(admin.ModelAdmin):
    list_display = ("reason", "amount", "currency")
    search_fields = ("reason",)
    class Media:
        css = {'all': ('admin_custom.css',)}
