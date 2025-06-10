from django.db import models
from django.conf import settings
from payments.models import Payment
from vehicles.models import Vehicle

class DocumentRenewal(models.Model):
    DOCUMENT_TYPES = [
        ("insurance", "Assurance"),
        ("registration", "Carte grise"),
        ("inspection", "Contrôle technique")
    ]

    CURRENCIES = [
        ("HTG", "HTG"), ("USD", "USD"), ("BTG", "BTG"), ("BTC", "BTC"), ("USDT", "USDT")
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="renewals")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="renewals")
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=5, choices=CURRENCIES)
    expiration_date = models.DateField()
    renewed_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    payment = models.OneToOneField(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True, null=True)

    def mark_as_paid(self, payment):
        self.paid = True
        self.payment = payment
        self.save()

    def __str__(self):
        return f"{self.document_type.title()} - {self.amount} {self.currency}"