from decimal import Decimal
from datetime import date
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from .querysets import ContractQuerySet


class ServiceType(models.Model):
    name = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name="Tip Sèvis"
    )
        
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Deskripsyon"
    )
    
    default_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2
    )
    
    is_active = models.BooleanField(
        default=True
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class Contract(models.Model):

    CONTRACT_SELL = "sell"
    CONTRACT_RENT = "rent"
    CONTRACT_LOAN = "loan"
    CONTRACT_SERVICE = "service"

    CONTRACT_TYPE_CHOICES = [
        (CONTRACT_SELL, "Vente"),
        (CONTRACT_RENT, "Location"),
        (CONTRACT_LOAN, "Prêt"),
        (CONTRACT_SERVICE, "Service"),
    ]

    CONTRACT_PENDING = "pending"
    CONTRACT_DRAFTED = "drafted"
    CONTRACT_COMPLETED = "completed"
    CONTRACT_CANCELLED = "cancelled"

    CONTRACT_STATUS_CHOICES = [
        (CONTRACT_PENDING, "En cours"),
        (CONTRACT_DRAFTED, "En négociation"),
        (CONTRACT_COMPLETED, "Complété"),
        (CONTRACT_CANCELLED, "Annulé"),
    ]

    objects = ContractQuerySet.as_manager()

    contract_type = models.CharField(
        max_length=20, 
        choices=CONTRACT_TYPE_CHOICES,
        default=CONTRACT_SELL,
        verbose_name="Tip Kontra"
    )
    
    contract_status = models.CharField(
        max_length=20,
        choices=CONTRACT_STATUS_CHOICES,
        default=CONTRACT_PENDING,
        verbose_name="Estati"
    )

    vehicle = models.ForeignKey(
        "vehicles.Vehicle", 
        on_delete=models.CASCADE, 
        related_name="contracts"
    )

    old_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="contracts_as_old"
    )

    new_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="contracts_as_new"
    )

    business = models.ForeignKey(
        "users.BusinessProfile",
        on_delete=models.SET_NULL,
        null=True, 
        blank=True
    )

    created_by_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owner_created_contracts"
    )

    created_by_employee = models.ForeignKey(
        "users.Employee",
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name="employee_created_contract"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # Paiement
    price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True,
        blank=True
    )
    
    is_paid = models.BooleanField(
        default=False
    )

    # Service
    service_type = models.ForeignKey(
    "contracts.ServiceType",
    null=True, 
    blank=True,
    on_delete=models.SET_NULL
    )

      # Vente
    warranty_period = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        verbose_name="Garanti",
        help_text="Durée de garantie"
    )
    
    # Location
    start_date = models.DateField(
        null=True,
        blank=True
    )
    
    end_date = models.DateField(
        null=True, 
        blank=True
    )
    
    return_date = models.DateField(
        null=True,
        blank=True
    )
    
    penalty_per_day = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True,
        blank=True
    )
    
    penalty_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal("0.00")
    )

    notes = models.TextField(
        blank=True, 
        null=True
    )

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        errors = {}

        if self.contract_type == self.CONTRACT_SERVICE:
            if not self.service_type:
                errors["service_type"] = "Type de service requis"
            if not self.price and self.service_type:
                self.price = self.service_type.default_price

        if self.contract_type == self.CONTRACT_RENT:
            if not self.start_date or not self.end_date:
                errors["start_date"] = "Dates requises pour la location"
            if self.end_date and self.start_date and self.end_date <= self.start_date:
                errors["end_date"] = "La date de fin doit être postérieure"
            if not self.penalty_per_day:
                errors["penalty_per_day"] = "Pénalité obligatoire"

        if errors:
            raise ValidationError(errors)

    def calculate_penalty(self, returned_date: date | None = None):
        if self.contract_type != self.CONTRACT_RENT:
            return Decimal("0.00")
        if not returned_date or not self.end_date:
            return Decimal("0.00")
        if returned_date <= self.end_date:
            return Decimal("0.00")
        days = (returned_date - self.end_date).days
        return days * (self.penalty_per_day or Decimal("0.00"))

    def save(self, *args, **kwargs):
        if self.contract_type == self.CONTRACT_RENT and self.return_date:
            self.penalty_amount = self.calculate_penalty(self.return_date)
        super().save(*args, **kwargs)