from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import timedelta
import uuid

User = get_user_model()

CURRENCY_CHOICES = [("HTG", "HTG"), ("USD", "USD"), ("BTG", "BTG")]


class Violation(models.Model):
    reason = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=5, choices=CURRENCY_CHOICES)
    driver_license = models.ImageField(upload_to="fine_images/", blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.reason} - {self.amount} {self.currency}"


class Fine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="fines")
    fine_id = models.CharField(max_length=100, unique=True, blank=True)
    driver_license = models.CharField(max_length=50, blank=True, null=True)
    vehicle = models.ForeignKey("vehicles.Vehicle", on_delete=models.CASCADE, related_name="fines")
    violation = models.ForeignKey(Violation, on_delete=models.SET_NULL, null=True, related_name="fines")
    currency = models.CharField(max_length=5, choices=CURRENCY_CHOICES)
    base_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    violation_date = models.DateField()
    reason = models.TextField(blank=True, null=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    penalty_applied_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.fine_id:
            self.fine_id = f"FINE-{uuid.uuid4().hex[:10].upper()}"
        if not self.due_date:
            self.due_date = (self.issued_at or timezone.now()).date() + timedelta(days=15)
        super().save(*args, **kwargs)

    @property
    def amount_with_penalty(self):
        if self.is_paid:
            return self.base_amount

        now = timezone.now().date()
        if not self.due_date or now <= self.due_date:
            return self.base_amount

        months_late = (now.year - self.due_date.year) * 12 + now.month - self.due_date.month
        if now.day < self.due_date.day:
            months_late -= 1

        if months_late <= 0:
            return self.base_amount

        penalty_rate = Decimal("0.03")
        amount = self.base_amount * ((1 + penalty_rate) ** months_late)
        return amount.quantize(Decimal("0.01"))

    def __str__(self):
        return f"{self.fine_id} - {self.violation.reason if self.violation else 'No Reason'}"


class FinePay(models.Model):
    fine = models.OneToOneField(Fine, on_delete=models.CASCADE, related_name="payment")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="fine_user")
    vehicle = models.ForeignKey("vehicles.Vehicle", on_delete=models.CASCADE, related_name="fine_vehicle")
    driver_license = models.ImageField(upload_to="permis/", blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=5, choices=CURRENCY_CHOICES)
    paid = models.BooleanField(default=False)
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction = models.OneToOneField("payments.Transaction", on_delete=models.SET_NULL, null=True, blank=True)

    def process_payment(self):
        balance = getattr(self.user, 'balance', None)
        if not balance or balance.total_balance() < self.amount:
            return False

        from payments.models import Transaction  # Import local pour éviter les problèmes circulaires

        balance.debit(self.amount, self.currency)
        transaction = Transaction.objects.create(
            user=self.user,
            amount=self.amount,
            currency=self.currency,
            status="Completed"
        )

        self.transaction = transaction
        self.paid = True
        self.save()

        self.fine.is_paid = True
        self.fine.save()

        self.send_invoice()
        return True

    def send_invoice(self):
        subject = "Konfimasyon Peman Amann"
        message = (
            f"Mr/Mme {self.user.email},\n\n"
            f"Ou peye amann pou: {self.fine.violation.reason if self.fine.violation else 'Rezon enkoni'}.\n"
            f"Kantite: {self.amount} {self.currency}\n"
            f"Dat: {self.payment_date.strftime('%Y-%m-%d')}\n\n"
            f"Mèsi anpil."
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.user.email], fail_silently=False)

    def __str__(self):
        return f"Ou peye {self.amount} {self.currency} pou kontravansyon #{self.fine.fine_id}"


class DeletedFine(models.Model):
    original_id = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=255)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='deleted_fines')
    delete_reason = models.TextField()
    deleted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'deleted_fines'

    def save(self, *args, **kwargs):
        kwargs['using'] = 'archive'  # Assure l’utilisation de la base "archive"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Deleted Fine {self.original_id} - {self.amount} by {self.deleted_by}"
