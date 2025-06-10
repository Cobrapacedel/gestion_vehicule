from django.db import models
from django.utils import timezone
from django.conf import settings
import random
from datetime import timedelta


class OTP(models.Model):
    OTP_TYPES = (
        ('login', 'Connexion'),
        ('payment', 'Paiement'),
        ('reset_password', 'Réinitialisation de mot de passe'),
    )

    DELIVERY_METHODS = (
        ('email', 'Email'),
        ('sms', 'SMS'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="otp")
    code = models.CharField(max_length=6)
    otp_type = models.CharField(max_length=20, choices=OTP_TYPES)  # renommé depuis 'type'
    delivery_method = models.CharField(max_length=10, choices=DELIVERY_METHODS, default="email")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)  # nouveau champ
    is_used = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'otp_type']),
            models.Index(fields=['code']),
        ]

    def __str__(self):
        return f"OTP {self.code} ({self.otp_type}) pour {self.user.email} via {self.delivery_method}"
        

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=5)
        super().save(*args, **kwargs)

    def is_valid(self):
        if not self.expires_at:
            return False
        return timezone.now() < self.expires_at

    def mark_as_used(self):
        self.is_used = True
        self.save(update_fields=["is_used"])

    @staticmethod
    def generate_code():
        while True:
            code = f"{random.randint(100000, 999999)}"
            if not OTP.objects.filter(code=code, is_used=False).exists():
                return code

    @classmethod
    def create_otp(cls, user, otp_type, delivery_method):
        code = cls.generate_code()
        expires = timezone.now() + timezone.timedelta(minutes=5)
        otp = cls.objects.create(
            user=user,
            code=code,
            otp_type=otp_type,
            delivery_method=delivery_method,
            expires_at=expires
        )
        return otp