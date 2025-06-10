from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Toll(models.Model):
    name = models.CharField(max_length=100)
    highway_name = models.CharField(max_length=150, blank=True)
    region = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.name} ({self.highway_name})"

    class Meta:
        verbose_name = "Poste de péage"
        verbose_name_plural = "Postes de péage"
        ordering = ['name']


class TollBooth(models.Model):
    toll = models.ForeignKey(Toll, on_delete=models.CASCADE, related_name='booths')
    booth_number = models.CharField(max_length=20)
    location = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.toll.name} - Guichet {self.booth_number}"

    class Meta:
        verbose_name = "Guichet de péage"
        verbose_name_plural = "Guichets de péage"
        unique_together = ('toll', 'booth_number')
        ordering = ['toll__name', 'booth_number']


class TollPayment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En traitement'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé'),
    ]

    CURRENCY_CHOICES = [
        ('HTG', 'Gourde'),
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Espès'),
        ('card', 'Kat'),
        ('mobile', 'Mobil'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='toll_payments')
    toll_booth = models.ForeignKey(TollBooth, on_delete=models.PROTECT, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='HTG')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Peman {self.amount} {self.currency} pou {self.user}"

    class Meta:
        verbose_name = "Paiement de péage"
        verbose_name_plural = "Paiements de péage"
        ordering = ['-created_at']


class TollTransaction(models.Model):
    TRANSACTION_STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('success', 'Succès'),
        ('failed', 'Échec'),
        ('refunded', 'Remboursé'),
        ('error', 'Erreur technique'),
    ]

    payment = models.OneToOneField(TollPayment, on_delete=models.CASCADE, related_name='transaction')
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES)
    confirmed_at = models.DateTimeField(auto_now_add=True)
    response_data = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.status}"

    class Meta:
        verbose_name = "Transaction de péage"
        verbose_name_plural = "Transactions de péage"
        ordering = ['-confirmed_at']
        
class TollDetection(models.Model):
    plate_number = models.CharField(max_length=15)
    detected_at = models.DateTimeField(auto_now_add=True)
    booth = models.ForeignKey(TollBooth, on_delete=models.CASCADE)
    processed = models.BooleanField(default=False)
    
class TollDebt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    interest_applied = models.BooleanField(default=False)
    remaining_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    is_fully_paid = models.BooleanField(default=False)