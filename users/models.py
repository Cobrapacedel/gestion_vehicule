import os
from datetime import timedelta
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from PIL import Image
from .querysets import ClientQuerySet, EmployeeQuerySet
from .managers import ClientManager, EmployeeManager

# ============================================================
# MANAGER
# ============================================================
class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Imèl la obligatwa")

        email = self.normalize_email(
            email
        )
        
        role = extra_fields.get(
            "role", 
            "user"
        )

        BUSINESS_ROLES = {"dealer", "agency", "garage"}
        extra_fields["user_type"] = "business" if role in BUSINESS_ROLES else "simple"

        user = self.model(
            email=email, 
            **extra_fields
        )
        
        user.set_password(
            password
        )
        
        user.save(
            using=self._db
        )

        # Création automatique du profil
        if user.user_type == "simple":
            SimpleProfile.objects.create(user=user)
        else:
            BusinessProfile.objects.create(
                user=user,
                business_name=email.split("@")[0]
            )

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "user")
        extra_fields.setdefault("user_type", "simple")
        return self.create_user(email, password, **extra_fields)


# ============================================================
# TYPES DE MÉTIERS (rôles dynamiques)
# ============================================================
class UserType(models.Model):
    name = models.CharField(
        max_length=30,
        unique=True
    )
    
    label = models.CharField(
        max_length=50
    )

    class Meta:
        verbose_name = "Type métier"
        verbose_name_plural = "Types métiers"

    def __str__(self):
        return self.label


# ============================================================
# UTILISATEUR
# ============================================================
class CustomUser(AbstractBaseUser, PermissionsMixin):
    
    AGENCY = "agency"
    DEALER = "dealer"
    GARAGE = "garage"
    

    ROLE_CHOICES = [
        (DEALER, "Konsesyonè"),
        (AGENCY, "Ajans Lokasyon"),
        (GARAGE, "Garaj"),
    ]
    
    SIMPLE = "simple"
    BUSINESS = "business"

    USER_TYPE_CHOICES = [
        (SIMPLE, "Senp Itilizatè"),
        (BUSINESS, "Biznis"),
    ]

    email = models.EmailField(
        unique=True, 
        db_index=True, 
        verbose_name="Imèl"
    )
    
    phone = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        validators=[RegexValidator(r"^\+?\d{8,15}$")],
        verbose_name="Telefòn"
    )
    
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default=DEALER
    )
    
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES, 
        default=SIMPLE
    )
    

    # Rôles métiers modifiables (UNIQUEMENT pour utilisateur simple)
    extra_roles = models.ManyToManyField(
        UserType,
        blank=True,
        related_name="users",
        verbose_name="Rôles métiers"
    )

    is_active = models.BooleanField(
        default=True
    )
        
    is_staff = models.BooleanField(
        default=False
    )
    
    invitation_code = models.CharField(
        max_length=12,
        unique=True, 
        blank=True,
        null=True
    )
    
    referred_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="referrals"
    )

    email_verified = models.BooleanField(
        default=False
    )
    
    phone_verified = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        default=timezone.now
    )
    
    updated_at = models.DateTimeField(
        auto_now=True
    )

    last_failed_login = models.DateTimeField(
        null=True,
        blank=True
    )
    
    last_login_ip = models.GenericIPAddressField(
        null=True, 
        blank=True
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone"]

    class Meta:
        verbose_name = "Itilizatè"
        verbose_name_plural = "Itilizatè"

    def __str__(self):
        return self.email

    # 🔐 Sécurité métier centrale
    def clean(self):
        super().clean()

    # 🧠 Helpers
    def has_role(self, role_name):
        return self.extra_roles.filter(name=role_name).exists()
    
    def save(self, *args, **kwargs):
        if not self.invitation_code:
            self.invitation_code = self.generate_invitation_code()
        super().save(*args, **kwargs)

    def generate_invitation_code(self):
        import secrets
        return secrets.token_hex(6)

    @property
    def is_simple(self):
        return self.user_type == "simple"

    @property
    def is_business(self):
        return self.user_type == "business"


# ============================================================
# PROFIL UTILISATEUR SIMPLE
# ============================================================
def default_avatar():
    return "avatars/default.png"


class SimpleProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="simple"
    )

    first_name = models.CharField(
        max_length=50,
        blank=True
    )
    
    last_name = models.CharField(
        max_length=50,
        blank=True
    )

    avatar = models.ImageField(
        upload_to="avatars/", 
        default=default_avatar
    )
    
    address = models.TextField(
        blank=True,
        null=True
    )

    driver_license_number = models.CharField(
        max_length=50,
        blank=True, 
        null=True
    )
    
    driver_license_image = models.ImageField(
        upload_to="driver_licenses/",
        blank=True, 
        null=True
    )

    email_notifications = models.BooleanField(
        default=True
    )
    
    sms_notifications = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.user.email

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.avatar:
            try:
                img = Image.open(self.avatar.path)
                img.thumbnail((300, 300))
                img.save(self.avatar.path)
            except Exception:
                pass


# ============================================================
# PROFIL BUSINESS
# ============================================================
class BusinessProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="businessprofile"
    )

    business_name = models.CharField(
        max_length=255
    )
    
    avatar = models.ImageField(
        upload_to="avatars/", 
        default=default_avatar
    )
    
    address = models.CharField(
        max_length=255,
        blank=True
    )

    patente_number = models.CharField(
        max_length=50,
        blank=True, 
        null=True
    )
    
    patente_image = models.ImageField(
        upload_to="patentes/",
        blank=True, 
        null=True
    )

    web_site = models.URLField(
        blank=True,
        null=True
    )

    email_notifications = models.BooleanField(
        default=True
        )
        
    sms_notifications = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.business_name
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.avatar:
            try:
                img = Image.open(self.avatar.path)
                img.thumbnail((300, 300))
                img.save(self.avatar.path)
            except Exception:
                pass

# ============================================================
#  CLIENT
# ============================================================
class Client(models.Model):
    USER = "user"
    DEALER = "dealer"
    AGENCY = "agency"
    GARAGE = "garage"
    
    CLIENT_TYPE_CHOICES = [
        (USER, "Senp Itilizatè"),
        (DEALER, "Konsesyonè"),
        (AGENCY, "Ajans Lokasyon"),
        (GARAGE, "Garaj"),
    ]
    
    owner = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="clients",
    verbose_name="Pwopriyetè"
)
    first_name = models.CharField(
        max_length=50,
        verbose_name="Non"
    )
    
    last_name = models.CharField(
        max_length=50,
        verbose_name="Siyati"
    )

    email = models.EmailField(
        blank=True,
        verbose_name="Imèl"
    )
    
    phone = models.CharField(
        max_length=25,
        verbose_name="Telefòn"
    )
    
    driver_license_number = models.CharField(
        max_length=50, blank=True, 
        null=True,
        verbose_name="Nimewo Lisans"
    )

    user_types = models.ManyToManyField(
        UserType, 
        blank=True,
        verbose_name="Tip Metye"
    )
    
    business_name = models.CharField(
        max_length=255,
        blank=True, 
        null=True,
        verbose_name="Non Biznis"
    )

    address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Adrès"
    )

    patente_number = models.CharField(
        max_length=50,
        blank=True, 
        null=True,
        verbose_name="Nimewo Pantant"
    )

    web_site = models.URLField(
        blank=True, 
        null=True,
        verbose_name="Sitwèb"
    )
    
    objects = ClientManager()

    client_type = models.CharField(
        max_length=20,
        choices=CLIENT_TYPE_CHOICES, default=USER,
        verbose_name="Tip Kliyan"
    )

    is_anonymous = models.BooleanField(
        default=False
    )

    real_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="as_client",
        verbose_name="Kliyan" 
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="created_clients", verbose_name="Non"
    )

    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Dat"
    )

    def __str__(self):
        
        return f"{self.first_name} {self.last_name}"


# ============================================================
#  EMPLOYE
# ============================================================
class Employee(models.Model):
    DD = "dd"
    RH = "rh"
    IT = "it"
    AC = "ac"
    MC = "mc"
    
    EMPLOYEE_TYPE_CHOICES = [
        (DD, "Directeur Départemental"),
        (RH, "Ressources Humaines"),
        (IT, "Département Informatique"),
        (AC, "Comptabilité"),
        (MC, "Mecanécanicien")
    ]

    business = models.ForeignKey(
        BusinessProfile,
        on_delete=models.CASCADE,
        related_name='employees',
        verbose_name="Biznis"
    )
    
    objects = EmployeeManager()

    employee_type = models.CharField(
        max_length=20,
        choices=EMPLOYEE_TYPE_CHOICES, default=DD,
        verbose_name="Tip Anplwaye"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Anplwaye"
    )

    first_name = models.CharField(
        max_length=255,
        verbose_name="Non"
    )
    
    last_name = models.CharField(
        max_length=255,
        verbose_name="Siyati"
    )

    email = models.EmailField(
        blank=True, 
        null=True,
        verbose_name="Imèl"
    )
   
    phone = models.CharField(
        max_length=50,
        blank=True, 
        null=True,
        verbose_name="Telefòn"
    )
    
    address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Adrès"
    )

    position = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Pòs"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Dat"
    )

    class Meta:
        
        ordering = ['first_name']

    def __str__(self):
        
        return f"{self.first_name} {self.last_name} ({self.business.business_name})"


# ============================================================
#  LOGIN ATTEMPT
# ============================================================
class LoginAttempt(models.Model):
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, 
        related_name="login_attempts"
    )

    failed_attempts = models.IntegerField(
        default=0
    )

    last_attempt = models.DateTimeField(
        auto_now_add=True
    )
    
    locked_until = models.DateTimeField(
        null=True, 
        blank=True
    )

    timestamp = models.DateTimeField(
        default=timezone.now
    )
    
    is_successful = models.BooleanField(
        default=True
    )

    def is_locked(self):
        
        return self.locked_until and timezone.now() < self.locked_until

    def __str__(self):
        
        return f"Tentatives – {self.user.email}"


# ============================================================
#  LOGIN HISTORY
# ============================================================
class LoginHistory(models.Model):
    
    MOBILE = "mobile"
    DESKTOP = "desktop"
    TABLET = "tablet"
    UNKNOWN = "unknown"

    DEVICE_TYPES = [
        (MOBILE, "Mobile"),
        (DESKTOP, "Ordinateur"),
        (TABLET, "Tablette"),
        (UNKNOWN, "Inconnu"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="login_histories"
    )

    ip_address = models.GenericIPAddressField(
        null=True, 
        blank=True
    )

    user_agent = models.TextField(
        blank=True, 
        null=True
    )

    city = models.CharField(
        max_length=255,
        blank=True, 
        null=True
    )
    
    country = models.CharField(
        max_length=255,
        blank=True, 
        null=True
    )

    device_type = models.CharField(
        max_length=55,
        choices=DEVICE_TYPES,
        default=MOBILE
    )

    timestamp = models.DateTimeField(
        default=timezone.now
    )

    class Meta:
        
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user.email} - {self.timestamp}"