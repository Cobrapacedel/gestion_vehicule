from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

# ==========================
# Document
# ==========================
class Document(models.Model):
    INSURANCE = "insurance"
    REGISTRATION = "registration"
    LICENSE = "license"
    OTHER = "other"
    
    DOCUMENT_TYPES = [
        (INSURANCE, "Asirans"),
        (REGISTRATION, "Kat Griz"),
        (LICENSE, "Lisans"),
        (OTHER, "Lòt"),
    ]


    document_type = models.CharField(
        verbose_name="Tip Dokiman", 
        max_length=20, 
        choices=DOCUMENT_TYPES,
        default=LICENSE
    )
    
    mandatory = models.BooleanField(
        verbose_name="Mandatè", 
        default=False
    )
        
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="documents"
    )
    
    vehicle = models.ForeignKey(
        "vehicles.Vehicle",
        on_delete=models.CASCADE,
        related_name="documents",
        blank=True,
        null=True,
        verbose_name="Veyikil"
    )
    
    file = models.FileField(
        verbose_name="Fichye", 
        upload_to="documents/%Y/%m/"
    )
    
    expiry_date = models.DateField(
        verbose_name="Dat Ekspirasyon", 
        blank=True, 
        null=True
    )
    
    is_valid = models.BooleanField(
        verbose_name="Valid", 
        default=True
    )
    
    is_paid = models.BooleanField(
        verbose_name="Peye", 
        default=False
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name ="Dokiman"
        verbose_name_plural = "Dokiman"

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.user}"

    def clean(self):
        if self.expiry_date and self.expiry_date < timezone.now().date():
            raise ValidationError("Dat dekspirasyon an pa dwe nan le pase .")

# ==========================
# Renouvellement de document
# ==========================
class DocumentRenewal(models.Model):
    document = models.ForeignKey(
        "documents.Document", 
        on_delete=models.CASCADE, 
        related_name="renewals"
    )
    
    vehicle = models.ForeignKey(
        "vehicles.Vehicle",
        on_delete=models.CASCADE,
        related_name="renewals"
    )
    
    old_expiry = models.DateField(
        verbose_name="Ansyen dat dekspirasyon"
    )
    
    is_paid = models.BooleanField(
        verbose_name="Peye", 
        default=False
    )
    
    new_expiry = models.DateField(
        verbose_name="Nouvo dat dekspirasyon"
    )
    
    renewed_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-renewed_at"]
        verbose_name ="Renouvle Dokiman"
        verbose_name_plural = "Renouvele Dikiman"

    def __str__(self):
        return f"{self.document} → {self.new_expiry}"