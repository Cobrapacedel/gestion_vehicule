import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

# ======================================================
# CONFIG
# ======================================================
LEDGER_DECIMAL_PLACES = 18
LEDGER_PRECISION = Decimal("1." + "0" * 18)

# ======================================================
# 💰 BALANCE (COMPTE PRINCIPAL UTILISATEUR)
# ======================================================
class Balance(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="balance"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Balance({self.user})"

    def get_currency(self, currency):
        currency = currency.lower()
        obj, _ = BalanceCurrency.objects.get_or_create(
            balance=self,
            currency=currency
        )
        return obj

    @transaction.atomic
    def credit(self, amount, currency):
        bc = self.get_currency(currency)
        amount = Decimal(str(amount)).quantize(LEDGER_PRECISION)
        bc.amount += amount
        bc.save(update_fields=["amount"])

    @transaction.atomic
    def debit(self, amount, currency):
        bc = self.get_currency(currency)
        amount = Decimal(str(amount)).quantize(LEDGER_PRECISION)
        if bc.amount < amount:
            raise ValueError("Solde insuffisant")

        amount = Decimal(str(amount)).quantize(LEDGER_PRECISION)
        bc.amount -= amount
        bc.save(update_fields=["amount"])


# ======================================================
# 💱 BALANCE PAR DEVISE
# ======================================================
class BalanceCurrency(models.Model):
    JMU = "jmu"
    HTG = "htg"
    USD = "usd"
    
    CURRENCY_TYPES = [
        (JMU, "JMU"),
        (HTG, "HTG"),
        (USD, "USD"),
        ]
        
    balance = models.ForeignKey(
        Balance,
        on_delete=models.CASCADE,
        related_name="currencies"
    )

    currency = models.CharField(
        max_length=10,
        choices=CURRENCY_TYPES,
        default=JMU
    )

    amount = models.DecimalField(
        max_digits=30,
        decimal_places=LEDGER_DECIMAL_PLACES,
        default=Decimal("0")
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        unique_together = ("balance", "currency")

    def __str__(self):
        return f"{self.balance.user} | {self.amount} {self.currency}"


# ======================================================
# 📜 TRANSACTIONS (LEDGER / AUDIT)
# ======================================================
class Transaction(models.Model):
    SIGNUP = "signup"
    REFERRAL = "referral"
    PAYMENT = "payment_success"
    CREATE_VEHICLE = "create_first_vehicle"
    BONUS = "bonus"
    DAILY_LOGIN = "daily_login"
    RANDOM = "random"
    CONTRACT = "contract"
    TRANSFER = "transfer"

    BONUS_TYPE = [
        (SIGNUP, "Création de compte"),
        (REFERRAL, "Parrainage"),
        (PAYMENT, "Paiement"),
        (CREATE_VEHICLE, "Création du Premier Vehiéhicule"),
        (RANDOM, "Aléatoire"),
        (DAILY_LOGIN, "Bonus quotidien"),
        (CONTRACT, "Contrat"),
        (TRANSFER, "Transfert"),
    ]

    CREDIT = "CREDIT"
    DEBIT = "DEBIT"
    
    TRANSACTION_TYPES = [
        (CREDIT, "ajoute"),
        (DEBIT, "retire")
    ]

    SYSTEM = "SYSTEM"
    USER = "USER"
    ADMIN = "ADMIN"
    
    SOURCES = [
        (SYSTEM, "Système"), 
        (USER, "Utilisateur"), 
        (ADMIN, "Administrateur")
    ]

    STATUS_PENDING = "pending"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "En attente"),
        (STATUS_COMPLETED, "Réussi"),
        (STATUS_FAILED, "Échoué"),
    ]
    
    JMU = "jmu"
    HTG = "htg"
    USD = "usd"
    
    CURRENCY_TYPES = [
        (JMU, "JMU"),
        (HTG, "HTG"),
        (USD, "USD"),
        ]

    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions",
    )

    amount = models.DecimalField(
        max_digits=30,
        decimal_places=LEDGER_DECIMAL_PLACES,
    )

    currency = models.CharField(
        max_length=10,
        choices=CURRENCY_TYPES,
        default=JMU
    )

    bonus_type = models.CharField(
        max_length=30,
        choices=BONUS_TYPE,
        default=SIGNUP
    )

    transaction_type = models.CharField(
        max_length=30,
        choices=TRANSACTION_TYPES,
        default=CREDIT
    )

    source = models.CharField(
        max_length=10,
        choices=SOURCES,
        default=USER
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    description = models.TextField(
        blank=True,
        null=True
    )
    
    metadata = models.JSONField(
        default=dict, 
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user} | {self.bonus_type} | {self.amount} {self.currency}"


# ======================================================
# 💳 PAYMENT (PAIEMENT INTERNE)
# ======================================================
class Payment(models.Model):
    CRYPTO = "crypto"
    MOBILE = "mobile"
    BANK = "bank"

    METHOD_TYPES = [
        (CRYPTO, "Crypto"),
        (MOBILE, "Mobile Money"),
        (BANK, "Banque"),
    ]
    
    STATUS_PENDING = "pending"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "En attente"),
        (STATUS_COMPLETED, "Réussi"),
        (STATUS_FAILED, "Échoué"),
    ]
    
    JMU = "jmu"
    HTG = "htg"
    USD = "usd"
    
    CURRENCY_TYPES = [
        (JMU, "JMU"),
        (HTG, "HTG"),
        (USD, "USD"),
        ]
        
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    amount = models.DecimalField(
        max_digits=30,
        decimal_places=LEDGER_DECIMAL_PLACES
    )
    
    currency = models.CharField(
        max_length=10,
        choices=CURRENCY_TYPES,
        default=JMU
    )

    is_paid = models.BooleanField(
        default=False
    )

    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payment"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    
    method = models.CharField(
        max_length=20, 
        choices=METHOD_TYPES
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    paid_at = models.DateTimeField(
        null=True, 
        blank=True
    )

    def __str__(self):
        return f"Payment {self.amount} {self.currency} - {self.user}"


# ======================================================
# 🔋 RECHARGE (WALLET ➜ BALANCE)
# ======================================================
class Recharge(models.Model):
    CRYPTO = "crypto"
    MOBILE = "mobile"
    BANK = "bank"

    METHOD_TYPES = [
        (CRYPTO, "Crypto"),
        (MOBILE, "Mobile Money"),
        (BANK, "Banque"),
    ]
    
    STATUS_PENDING = "pending"
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "En attente"),
        (STATUS_SUCCESS, "Réussie"),
        (STATUS_FAILED, "Échouée"),
    ]
    
    JMU = "jmu"
    HTG = "htg"
    USD = "usd"
    
    CURRENCY_TYPES = [
        (JMU, "JMU"),
        (HTG, "HTG"),
        (USD, "USD"),
        ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recharges"
    )

    amount = models.DecimalField(
        max_digits=30,
        decimal_places=LEDGER_DECIMAL_PLACES
    )
    
    currency = models.CharField(
        max_length=10,
        choices=CURRENCY_TYPES,
        default=JMU
    )

    provider = models.CharField(
        max_length=50
    )
    
    reference = models.CharField(
        max_length=100, 
        unique=True
    )
    
    method = models.CharField(
        max_length=20, 
        choices=METHOD_TYPES,
        default=CRYPTO
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recharge"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    processed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Recharge {self.amount} {self.currency} - {self.user}"


# ======================================================
# 🔄 FUND TRANSFER (UTILISATEUR ➜ UTILISATEUR)
# ======================================================
class FundTransfer(models.Model):
    CRYPTO = "crypto"
    MOBILE = "mobile"
    BANK = "bank"

    METHOD_TYPES = [
        (CRYPTO, "Crypto"),
        (MOBILE, "Mobile Money"),
        (BANK, "Banque"),
    ]
    
    STATUS_PENDING = "pending"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "En attente"),
        (STATUS_COMPLETED, "Réussi"),
        (STATUS_FAILED, "Échoué"),
    ]
    
    JMU = "jmu"
    HTG = "htg"
    USD = "usd"
    
    CURRENCY_TYPES = [
        (JMU, "JMU"),
        (HTG, "HTG"),
        (USD, "USD"),
        ]
        
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4,
        editable=False
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_transfers"
    )

    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_transfers"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    amount = models.DecimalField(
        max_digits=30, 
        decimal_places=LEDGER_DECIMAL_PLACES
    )
    
    currency = models.CharField(
        max_length=10,
        choices=CURRENCY_TYPES,
        default=JMU
    )
    
    method = models.CharField(
        max_length=20, 
        choices=METHOD_TYPES,
        default=CRYPTO
    )

    sender_transaction = models.OneToOneField(
        Transaction,
        on_delete=models.SET_NULL,
        null=True,
        related_name="debit_transfer"
    )

    receiver_transaction = models.OneToOneField(
        Transaction,
        on_delete=models.SET_NULL,
        null=True,
        related_name="credit_transfer"
    )
    
    description = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.sender} ➜ {self.receiver} ({self.amount} {self.currency})"


# ======================================================
# 🔐 WALLET (EXTERNE)
# ======================================================
class Wallet(models.Model):
    CRYPTO = "crypto"
    MOBILE = "mobile"
    BANK = "bank"

    WALLET_TYPES = [
        (CRYPTO, "Crypto"),
        (MOBILE, "Mobile Money"),
        (BANK, "Banque"),
    ]
    
    BTC = "btc"
    ETH = "eth"
    BSC = "bsc"
    
    NETWORK_TYPES = [
        (BTC, "Bitcoin"),
        (ETH, "Ethereum"),
        (BSC, "Binance Smart Chain"),
        ]
        
    JMU = "jmu"
    HTG = "htg"
    USD = "usd"
    
    CURRENCY_TYPES = [
        (JMU, "JMU"),
        (HTG, "HTG"),
        (USD, "USD"),
        ]

    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallets"
    )
    
    balance = models.ForeignKey(
        Balance, 
        on_delete=models.SET_NULL,
        null=True,
        related_name="wallets")

    wallet_type = models.CharField(
        max_length=20, 
        choices=WALLET_TYPES,
        default=CRYPTO
    )

    network = models.CharField(
        max_length=50, 
        choices=NETWORK_TYPES,
        default=BTC
    )
    
    public_key = models.CharField(
        max_length=255,
        unique=True
    )
    
    address = models.CharField(
        max_length=255,
        unique=True
    )

    currency = models.CharField(
        max_length=10,
        choices=CURRENCY_TYPES,
        default=JMU
    )

    label = models.CharField(
        max_length=50, 
        blank=True
    )
    
    is_active = models.BooleanField(
        default=True
    )
    
    is_verified = models.BooleanField(
        default=False
    )

    metadata = models.JSONField(
        default=dict, 
        blank=True
        )
        
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ("user", "network", "public_key", "address")

    def __str__(self):
        return f"{self.user} | {self.network} | {self.address}"