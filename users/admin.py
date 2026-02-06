from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import (
    CustomUser,
    SimpleProfile,
    BusinessProfile,
    Client,
    Employee,
    LoginAttempt,
    LoginHistory,
)
from .forms import CustomUserCreationForm, CustomUserChangeForm


# ============================
# ADMIN : CUSTOM USER
# ============================
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = (
        "email",
        "phone",
        "user_type",
        "is_active",
        "is_staff",
        "last_login",
    )
    list_filter = ("user_type", "is_active", "is_staff")

    fieldsets = (
        ("Identifiants", {"fields": ("email", "phone", "password")}),
        ("Type utilisateur", {"fields": ("user_type",)}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "phone", "user_type", "password1", "password2"),
        }),
    )

    search_fields = ("email", "phone")
    ordering = ("email",)
    
    def save_model(self, request, obj, form, change):
        if not change:  # création via admin
            obj.created_via_admin = True
        super().save_model(request, obj, form, change)


# ================================
# ADMIN : PROFILE UTILISATEUR SIMPLE
# ================================
@admin.register(SimpleProfile)
class SimpleProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "first_name",
        "last_name",
        "address",
        "driver_license_number",
        "driver_license_preview",
    )

    def driver_license_preview(self, obj):
        if obj.driver_license_image:
            return format_html(
                '<img src="{}" width="60" style="border-radius:5px;" />',
                obj.driver_license_image.url,
            )
        return "Aucune image"
    driver_license_preview.short_description = "Permis (photo)"

    search_fields = ("user__email", "first_name", "last_name", "driver_license_number")


# ================================
# ADMIN : BUSINESS PROFILE
# ================================
@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "business_name",
        "address",
        "patente_number",
        "patente_preview",
    )

    def patente_preview(self, obj):
        if obj.patente_image:
            return format_html(
                '<img src="{}" width="60" style="border-radius:5px;" />',
                obj.patente_image.url,
            )
        return "Aucune image"
    patente_preview.short_description = "Patente (photo)"

    search_fields = ("user__email", "business_name", "patente_number")


# ============================
# ADMIN : CLIENT
# ============================
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("real_user", "created_at")
    search_fields = ("user__email",)


# ============================
# ADMIN : EMPLOYEE
# ============================
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "business", "user", "employee_type", "position", "created_at")
    search_fields = ("first_name", "business__business_name", "user__email", "position")
    list_filter = ("business", "position")

# ============================
# ADMIN : LOGIN ATTEMPTS
# ============================
@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "failed_attempts",
        "is_successful",
        "timestamp",
    )
    list_filter = ("is_successful", "timestamp")
    search_fields = ("user__email", "locked_until")


# ============================
# ADMIN : LOGIN HISTORY
# ============================
@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "ip_address",
        "city",
        "country",
        "timestamp",
        "device_type",
    )
    list_filter = ("country", "device_type")
    search_fields = ("user__email", "ip_address", "city", "country")