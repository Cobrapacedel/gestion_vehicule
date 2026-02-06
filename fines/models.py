from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import uuid


# ============================
# Constantes
# ============================
HTG = "htg"
USD = "usd"
JMU = "jmu"

CURRENCY_CHOICES = [
    (HTG, "HTG"),
    (USD, "USD"),
    (JMU, "JMU"),
]


# ============================
# Modèle Violation (référentiel)
# ============================

class Violation(models.Model):
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Code unique de la violation"
    )

    reason = models.CharField(
        max_length=255,
        help_text="Libellé de l’infraction"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    currency = models.CharField(
        max_length=5,
        choices=CURRENCY_CHOICES,
        default=HTG
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.reason} ({self.amount} {self.currency})"


# ============================
# Modèle Fine
# ============================

class Fine(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="fines_received",
        verbose_name="Pwopriyetè",
        help_text="Propriétaire du véhicule"
    )

    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fines_driven",
        verbose_name="Chofè",
        help_text="Conducteur au moment de l’infraction"
    )

    issuer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fines_issued",
        verbose_name="Ajan Otorize",
        help_text="Agent ou autorité"
    )

    fine_id = models.CharField(
        max_length=100,
        unique=True,
        blank=True
    )

    vehicle = models.ForeignKey(
        "vehicles.Vehicle",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="fines",
        verbose_name="Veyikil"
    )

    violation = models.ForeignKey(
        "fines.Violation",
        on_delete=models.PROTECT,
        related_name="fines",
        verbose_name="Enfraksyon"
    )

    issued_at = models.DateTimeField(
        auto_now_add=True
    )
    
    violation_date = models.DateField(
        auto_now_add=True
    )

    due_date = models.DateField(
        null=True,
        blank=True
    )

    is_paid = models.BooleanField(
        default=False
    )

    penalty_applied_at = models.DateTimeField(
        null=True,
        blank=True
    )

    note = models.TextField(
        blank=True,
        null=True,
        help_text="Observation ou note interne"
    )

    class Meta:
        ordering = ["-issued_at"]

    def save(self, *args, **kwargs):
        if not self.fine_id:
            self.fine_id = f"FINE-{uuid.uuid4().hex[:10].upper()}"

        if not self.due_date:
            self.due_date = (self.issued_at or timezone.now()).date() + timedelta(days=15)

        super().save(*args, **kwargs)

    @property
    def currency(self):
        return self.violation.currency

    @property
    def amount_with_penalty(self):
        if self.is_paid:
            return self.violation.amount

        today = timezone.now().date()

        if today <= self.due_date:
            return self.violation.amount

        months_late = (
            (today.year - self.due_date.year) * 12
            + today.month
            - self.due_date.month
        )

        if today.day < self.due_date.day:
            months_late -= 1

        if months_late <= 0:
            return self.violation.amount

        penalty_rate = Decimal("0.03")
        amount = self.violation.amount * ((1 + penalty_rate) ** months_late)

        return amount.quantize(Decimal("0.01"))

    def __str__(self):
        return f"{self.fine_id} | {self.owner}"


# ============================
# Modèle DeletedFine (archive)
# ============================

class DeletedFine(models.Model):
    original_id = models.IntegerField()

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="deleted_fines"
    )

    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deleted_fines_driven"
    )

    violation = models.ForeignKey(
        "fines.Violation",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="deleted_fines_violation")

    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="deleted_fines_by"
    )

    delete_reason = models.TextField()

    deleted_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        managed = True
        db_table = "deleted_fines"

    def save(self, *args, **kwargs):
        kwargs["using"] = "archive"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Kontravansyon {self.original_id} Efase"