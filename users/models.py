from django.db import models
import uuid
import secrets  # For better OTP generation
from django.utils import timezone
from datetime import timedelta
from django.core.validators import RegexValidator
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.conf import settings
import os
from PIL import Image
import logging
import requests
from otp.models import OTP

# Default Avatar Handling
def default_avatar():
    """Provide a default avatar path with a fallback to a static file."""
    default_path = os.path.join(settings.MEDIA_ROOT, "avatars/default.png")
    if not os.path.exists(default_path):
        return os.path.join(settings.STATIC_ROOT, "images/avatars/default.png")  # Fallback to static file
    return default_path

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email=email)

# Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Custom User Model"""
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone_number"]
    
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    email = models.EmailField(unique=True, null=False, blank=False)
    otp_preference = models.CharField(
        max_length=10,
        choices=[("email", "Email"), ("sms", "SMS")],
        default="email")
    phone_number = models.CharField(
        max_length=50, 
        unique=True, 
        validators=[RegexValidator(r"^\+?1?\d{9,15}$", "Numéro de téléphone invalide.")]
    )
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    driver_license = models.CharField(max_length=50, blank=True, null=True, verbose_name="Numéro de permis de conduire")
    last_failed_login = models.DateTimeField(null=True, blank=True)
    is_locked = models.BooleanField(default=False)  # For temporary account locking
    
    objects = CustomUserManager()
    
    EMAIL_FIELD = "email"

    def unlock_account(self):
        """Unlock a user account"""
        self.is_locked = False
        self.save(update_fields=["is_locked"])

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

# Profile Model
class Profile(models.Model):
    """User profile linked to CustomUser"""
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    address = models.TextField(blank=True, null=True)
    email_notifications = models.BooleanField(default=True)
    phone_number = models.CharField(
        max_length=15, 
        unique=True, 
        validators=[RegexValidator(r"^\+?1?\d{9,15}$", "Numéro de téléphone invalide.")]
    )
    avatar = models.ImageField(upload_to="avatars/", default="avatars/default.png")
    sms_notifications = models.BooleanField(default=False)

    def __str__(self):
        return f"Profil de {self.user.email}"

    def save(self, *args, **kwargs):
        """Supprime l'ancienne image avant d'enregistrer la nouvelle et redimensionne"""
        if self.pk:  # Vérifie si le profil existe déjà
            try:
                old_profile = Profile.objects.get(pk=self.pk)
                if old_profile.avatar and old_profile.avatar != self.avatar:
                    old_avatar_path = old_profile.avatar.path
                    if os.path.exists(old_avatar_path) and "default.png" not in old_avatar_path:
                        os.remove(old_avatar_path)  # Supprime l'ancienne image
            except Profile.DoesNotExist:
                pass  # Aucun ancien profil trouvé, donc pas d'image à supprimer

        super().save(*args, **kwargs)

        # Redimensionner l'image après la sauvegarde
        if self.avatar:
            img = Image.open(self.avatar.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.avatar.path)

    def delete(self, *args, **kwargs):
        """Supprime l'image associée lors de la suppression du profil"""
        if self.avatar and "default.png" not in self.avatar.path:
            if os.path.exists(self.avatar.path):
                os.remove(self.avatar.path)
        super().delete(*args, **kwargs)

# Login Attempt Management
class LoginAttempt(models.Model):
    """Manage failed login attempts"""
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="login_attempts")
    failed_attempts = models.IntegerField(default=0)
    last_attempt = models.DateTimeField(auto_now_add=True)
    locked_until = models.DateTimeField(null=True, blank=True)

    def is_locked(self):
        """Check if the user is temporarily locked"""
        return self.locked_until and timezone.now() < self.locked_until

    def register_failed_attempt(self):
        """Increment failed attempts and lock the user with progressive blocking"""
        self.failed_attempts += 1
        self.last_attempt = timezone.now()

        if self.failed_attempts >= 3:
            block_duration = min(2**(self.failed_attempts - 3) * 30, 3600)  # Progressive blocking (max 1 hour)
            self.locked_until = timezone.now() + timedelta(seconds=block_duration)
        
        self.save()

    def reset_attempts(self):
        """Reset failed attempts after a successful login"""
        self.failed_attempts = 0
        self.locked_until = None
        self.save()

    def __str__(self):
        return f"Tentatives de {self.user.email} : {self.failed_attempts}"

# Login History Model
class LoginHistory(models.Model):
    """History of successful logins"""
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.email} - {self.ip_address} ({self.timestamp})"

    @staticmethod
    def get_geolocation(ip_address):
        """Fetch geolocation data using an external API."""
        try:
            api_key = settings.IPSTACK_API_KEY  # Securely load from settings
            response = requests.get(f"http://api.ipstack.com/{ip_address}?access_key={api_key}", timeout=5)
            response.raise_for_status()
            data = response.json()
            return data.get("city"), data.get("country_name")
        except requests.RequestException as e:
            logging.error(f"Error with geolocation API: {e}")
            return None, None

    @classmethod
    def log_login(cls, user, ip_address, user_agent):
        """Log a successful login attempt."""
        city, country = cls.get_geolocation(ip_address)
        cls.objects.create(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            city=city,
            country=country
        )