from rest_framework import serializers
from .models import OTP


class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = ['id', 'user', 'code', 'otp_type', 'delivery_method', 'created_at', 'expires_at', 'is_used']
        read_only_fields = ['created_at', 'expires_at', 'is_used']