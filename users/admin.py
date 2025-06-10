from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile, LoginAttempt, LoginHistory

# Custom User Admin
class CustomUserAdmin(UserAdmin):
    """Customized admin interface for the CustomUser model."""
    list_display = (
        "email",
        "first_name",
        "last_name",
        "phone_number",
        "driver_license",
        "is_active",
        "is_staff",
        "is_locked",
        "created_at",
    )
    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "is_locked",
        "created_at",
    )
    search_fields = ("email", "first_name", "last_name", "phone_number", "driver_license")
    ordering = ("-created_at",)
    readonly_fields = ("uuid", "created_at", "last_failed_login")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "phone_number")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "is_locked")}),
        ("Important Dates", {"fields": ("created_at", "last_failed_login")}),
        ("Unique Identifier", {"fields": ("uuid",)}),
        ("Informations supplémentaires", {"fields": ("driver_license",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "phone_number", "driver_license", "password1", "password2"),
        }),
    )

# Profile Admin
class ProfileAdmin(admin.ModelAdmin):
    """Admin interface for the Profile model."""
    list_display = (
        "user",
        "address",
        "phone_number",
        "email_notifications",
        "sms_notifications",
    )
    list_filter = ("email_notifications", "sms_notifications")
    search_fields = ("user__email", "phone_number", "address")
    readonly_fields = ("user",)

# Login Attempt Admin
class LoginAttemptAdmin(admin.ModelAdmin):
    """Admin interface for the LoginAttempt model."""
    list_display = (
        "user",
        "failed_attempts",
        "last_attempt",
        "locked_until",
        "is_locked",
    )
    list_filter = ("failed_attempts", "locked_until")
    search_fields = ("user__email",)
    readonly_fields = ("user", "failed_attempts", "last_attempt", "locked_until")

    def is_locked(self, obj):
        """Display whether the user is currently locked."""
        return obj.is_locked()
    is_locked.boolean = True  # Display as a green/red checkbox

# Login History Admin
class LoginHistoryAdmin(admin.ModelAdmin):
    """Admin interface for the LoginHistory model."""
    list_display = (
        "user",
        "ip_address",
        "city",
        "country",
        "timestamp",
    )
    list_filter = ("city", "country", "timestamp")
    search_fields = ("user__email", "ip_address", "city", "country")
    readonly_fields = ("user", "ip_address", "user_agent", "city", "country", "timestamp")

# Register Models
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(LoginAttempt, LoginAttemptAdmin)
admin.site.register(LoginHistory, LoginHistoryAdmin)