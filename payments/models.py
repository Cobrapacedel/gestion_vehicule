from django.db import models
from django.conf import settings
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import uuid
from .utils import get_bsc_wallet_balance

# Pas d'import direct ici — on utilisera des chaînes pour éviter les cycles
# from documents.models import Document

def send_payment_notification(user, message=None):
    channel_layer = get_channel_layer()
    last_payment = user.payments.last()
    msg = message or f"Votre paiement de {last_payment.amount} {last_payment.currency} a été traité avec succès."
    async_to_sync(channel_layer.group_send)(
        f'notifications_{user.id}',
        {
            'type': 'send_notification',
            'message': msg
        }
    )

class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet")
    public_key = models.CharField(max_length=42, unique=True)
    network = models.CharField(max_length=30, choices=[
        ('bsc', 'Binance Smart Chain'),
        ('eth', 'Ethereum'),
        ('polygon', 'Polygon'),
    ])
    wallet_balance = models.DecimalField(max_digits=20, decimal_places=8, default=0)

    def update_balance(self):
        if self.network == "bsc":
            balance = get_bsc_wallet_balance(self.public_key)
            if balance is not None:
                self.wallet_balance = balance
                self.save()
        return self.wallet_balance
        
class Balance(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="balance")
    htg_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    usd_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    btg_balance = models.DecimalField(max_digits=18, decimal_places=8, default=0.00000000)
    btc_balance = models.DecimalField(max_digits=18, decimal_places=8, default=0.00000000)
    usdt_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def total_balance(self, rates=None):
        conversion_rates = rates or {
            "HTG": 1,
            "USD": 135,
            "BTG": 30 * 135,
            "BTC": 60000 * 135,
            "USDT": 135,
        }
        return (
            self.htg_balance +
            self.usd_balance * conversion_rates["USD"] +
            self.btg_balance * conversion_rates["BTG"] +
            self.btc_balance * conversion_rates["BTC"] +
            self.usdt_balance * conversion_rates["USDT"]
        )

    def credit(self, amount, currency):
        field = f"{currency.lower()}_balance"
        setattr(self, field, getattr(self, field) + amount)
        self.save()
        Transaction.objects.create(
            user=self.user,
            amount=amount,
            currency=currency,
            status="Completed",
            description="Crédit automatique"
        )

    def debit(self, amount, currency):
        field = f"{currency.lower()}_balance"
        if getattr(self, field) >= amount:
            setattr(self, field, getattr(self, field) - amount)
            self.save()
            Transaction.objects.create(
                user=self.user,
                amount=-amount,
                currency=currency,
                status="Completed",
                description="Débit automatique"
            )
            return True
        return False

    def __str__(self):
        return f"Solde de {self.user.email} (Total HTG : {self.total_balance():,.2f})"


class Transaction(models.Model):
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, choices=[("HTG", "HTG"), ("USD", "USD"), ("BTG", "BTG"), ("BTC", "BTC"), ("USDT", "USDT")])
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[("Pending", "Annatant"), ("Completed", "Reyisi"), ("Failed", "Echwe")], default="Pending")
    reference = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} {self.currency} ({self.status})"


class Payment(models.Model):
    PAYMENT_TYPES = [
        ("renewal", "Renouvle Dokiman"),
        ("fine", "Pèman Kontravansyon"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=5, choices=[("HTG", "HTG"), ("USD", "USD"), ("BTG", "BTG"), ("BTC", "BTC"), ("USDT", "USDT")])
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, db_index=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction = models.OneToOneField(Transaction, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.payment_type} - {self.amount} {self.currency}"


class Recharge(models.Model):
    RECHARGE_METHODS = [
        ("mobile", "Mobile Money"),
        ("card", "Kat Labank"),
        ("crypto", "Kripto"),
        ("bank", "Bank"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recharges")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=5, choices=[("HTG", "HTG"), ("USD", "USD"), ("BTG", "BTG"), ("BTC", "BTC"), ("USDT", "USDT")])
    method = models.CharField(max_length=20, choices=RECHARGE_METHODS)
    status = models.CharField(max_length=20, choices=[("Pending", "Annatant"), ("Completed", "Reyisi"), ("Failed", "Echwe")], default="Pending")
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    transaction = models.OneToOneField(Transaction, on_delete=models.SET_NULL, null=True, blank=True)

    def complete_recharge(self):
        if self.status != "Completed":
            self.status = "Completed"
            self.completed_at = timezone.now()
            self.save()
            self.user.balance.credit(self.amount, self.currency)
            send_payment_notification(self.user)

    def __str__(self):
        return f"Recharge {self.amount} {self.currency} via {self.method} - {self.status}"


class FundTransfer(models.Model):
    TRANSFER_METHODS = [
        ("mobile", "Mobile Money"),
        ("card", "Kat Labank"),
        ("crypto", "Kripto"),
        ("bank", "Bank"),
    ]
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_transfers')
    fund_transfer_id = models.CharField(max_length=9, blank=True)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_transfers')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=5, choices=[("HTG", "HTG"), ("USD", "USD"), ("BTG", "BTG"), ("BTC", "BTC"), ("USDT", "USDT")])
    method = models.CharField(max_length=20, choices=TRANSFER_METHODS)
    status = models.CharField(max_length=20, choices=[("Pending", "Annatant"), ("Completed", "Reyisi"), ("Failed", "Echwe")], default="Pending")
    description = models.CharField(max_length=255, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    transaction = models.OneToOneField(Transaction, on_delete=models.SET_NULL, null=True, blank=True)

    def complete_transfer(self):
        if self.status != "Completed":
            self.status = "Completed"
            self.completed_at = timezone.now()
            self.save()
            self.sender.balance.debit(self.amount, self.currency)
            self.recipient.balance.credit(self.amount, self.currency)
            send_payment_notification(self.sender, f"Vous avez envoyé {self.amount} {self.currency} à {self.recipient.username}.")
            send_payment_notification(self.recipient, f"Vous avez reçu {self.amount} {self.currency} de {self.sender.username}.")

    def __str__(self):
        return f"{self.sender} ➜ {self.recipient} | {self.amount} {self.currency}"