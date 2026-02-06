from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

# ============================
# POSTE DE PÉAGE
# ============================
class Toll(models.Model):
    HTG = "htg"
    USD = "usd"
    JMU = "jmu"
    
    CURRENCY_TYPE = [
        (HTG, "HTG"),
        (USD, "USD"),
        (JMU, "JMU")
    ]
    
    name = models.CharField(
        max_length=100
    )
    
    highway_name = models.CharField(
        max_length=150, 
        blank=True
    )
    
    region = models.CharField(
        max_length=100, 
        blank=True
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00")
    )

    currency = models.CharField(
        max_length=5,
        choices=CURRENCY_TYPE,
        default=HTG
    )

    class Meta:
        verbose_name = "Rout Pòs Peyaj"
        verbose_name_plural = "Rout Pòs Peyaj"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.highway_name})"


# ============================
# GUICHET / PASSAGE
# ============================

class TollBooth(models.Model):
    toll = models.ForeignKey(
        "tolls.Toll",
        on_delete=models.CASCADE,
        related_name="booths"
    )

    vehicle = models.ForeignKey(
        "vehicles.Vehicle",
        on_delete=models.CASCADE,
        related_name="vehicle_tolls"
    )

    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="driven_tolls"
    )

    booth_number = models.CharField(
        max_length=20
    )

    passage_date = models.DateTimeField(
        default=timezone.now
    )

    is_paid = models.BooleanField(
        default=False
    )

    class Meta:
        verbose_name = "Guichet de péage"
        verbose_name_plural = "Guichets de péage"
        ordering = ["-passage_date"]
        unique_together = ("toll", "booth_number")

    def __str__(self):
        return f"{self.toll.name} — Guichet {self.booth_number}"

    @property
    def owner(self):
        """Propriétaire réel du véhicule"""
        return self.vehicle.owner

    @property
    def amount(self):
        return self.toll.amount

    @property
    def currency(self):
        return self.toll.currency


# ============================
# DÉTECTION AUTOMATIQUE
# ============================

class TollDetection(models.Model):
    vehicle = models.ForeignKey(
        "vehicles.Vehicle",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="detections"
        )
    
    detected_at = models.DateTimeField(
        auto_now_add=True
    )

    booth = models.ForeignKey(
        "tolls.TollBooth",
        on_delete=models.CASCADE,
        related_name="detections"
    )

    processed = models.BooleanField(
        default=False
    )

    class Meta:
        ordering = ["-detected_at"]

    def __str__(self):
        return f"Détection {self.vehicle} @ {self.detected_at}"


# ============================
# DETTE DE PÉAGE
# ============================

class TollDebt(models.Model):
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="toll_debts"
    )

    booth = models.ForeignKey(
        "tolls.TollBooth",
        on_delete=models.CASCADE,
        related_name="debts"
    )

    amount_due = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    interest_rate = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal("0.03"),
        help_text="Taux mensuel"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        auto_now=True
    )

    is_fully_paid = models.BooleanField(
        default=False
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Dette {self.amount_due} "
            f"{self.booth.currency.upper()} — "
            f"Chauffeur: {self.driver}"
    )
        
    def clean(self):
        if not self.driver:
            raise ValidationError("Une dette doit être associée à un chauffeur.")

    def apply_interest(self):
        """Applique l'intérêt mensuel si impayé"""
        if self.is_fully_paid:
            return

        self.amount_due = (
            self.amount_due * (1 + self.interest_rate)
        ).quantize(Decimal("0.01"))

        self.save(update_fields=["amount_due"])
        
@property
def vehicle_owner(self):
    return self.booth.vehicle.owner