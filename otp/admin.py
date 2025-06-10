from django.contrib import admin
from .models import OTP

class OTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'delivery_method', 'get_expires_at', 'created_at')
    readonly_fields = ('code', 'delivery_method', 'get_expires_at', 'created_at')
    list_filter = ('delivery_method',)  # Pas 'expires_at' car ce n’est pas un champ

    def get_expires_at(self, obj):
        return obj.expires_at
    get_expires_at.short_description = "Expire le"

admin.site.register(OTP, OTPAdmin)