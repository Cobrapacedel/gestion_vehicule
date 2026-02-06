import uuid
import secrets
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction as db_transaction

from payments.models import Wallet, Balance, Transaction, LEDGER_PRECISION
from payments.services.balance_service import BalanceService


# ============================================================
# CONSTANTES
# ============================================================

SUPPORTED_NETWORKS = ("eth", "bsc", "btc", "tron", "polygon")


# ============================================================
# GÉNÉRATEURS
# ============================================================

def generate_wallet_uuid() -> str:
    return str(uuid.uuid4())


def generate_wallet_address(network: str) -> str:
    network = network.lower()

    if network in ("eth", "bsc", "polygon"):
        return "0x" + secrets.token_hex(20)

    if network == "btc":
        return "bc1" + secrets.token_hex(20)

    if network == "tron":
        return "T" + secrets.token_hex(20)

    raise ValidationError(f"Réseau non supporté : {network}")


# ============================================================
# CRÉATION DE WALLET
# ============================================================

@db_transaction.atomic
def create_wallet_for_user(user, network: str) -> Wallet:
    network = network.lower()

    if network not in SUPPORTED_NETWORKS:
        raise ValidationError("Réseau non autorisé")

    # Balance obligatoire
    balance, _ = Balance.objects.get_or_create(user=user)

    existing_wallet = Wallet.objects.filter(
        user=user,
        network=network,
        is_active=True
    ).first()

    if existing_wallet:
        return existing_wallet

    while True:
        public_key = generate_wallet_uuid()
        if not Wallet.objects.filter(public_key=public_key).exists():
            break

    wallet = Wallet.objects.create(
        user=user,
        balance=balance,
        network=network,
        public_key=public_key,
        address=generate_wallet_address(network),
        is_active=True,
    )

    return wallet


# ============================================================
# CREDIT WALLET (via BALANCE)
# ============================================================

@db_transaction.atomic
def credit_wallet(
    *,
    user,
    amount,
    currency: str,
    source=Transaction.SYSTEM,
    metadata=None,
    description=None,
) -> Transaction:
    """
    Crédit un wallet utilisateur via Balance (source de vérité)
    + enregistre une transaction ledger
    """

    currency = currency.lower()
    amount = Decimal(str(amount)).quantize(LEDGER_PRECISION)

    if amount <= 0:
        raise ValidationError("Montant invalide")

    # 1️⃣ Crédit balance
    BalanceService.credit(user, amount, currency)

    # 2️⃣ Ledger
    tx = Transaction.objects.create(
        user=user,
        amount=amount,
        currency=currency,
        transaction_type=Transaction.CREDIT,
        source=source,
        status=Transaction.STATUS_COMPLETED,
        metadata=metadata or {},
        description=description or f"Ou resevwa sou kont ou: {currency.upper()}",
    )

    return tx


# ============================================================
# DEBIT WALLET (via BALANCE)
# ============================================================

@db_transaction.atomic
def debit_wallet(
    *,
    user,
    amount,
    currency: str,
    source=Transaction.USER,
    metadata=None,
    description=None,
) -> Transaction:
    """
    Débite un wallet utilisateur via Balance
    + enregistre une transaction ledger
    """

    currency = currency.lower()
    amount = Decimal(str(amount)).quantize(LEDGER_PRECISION)

    if amount <= 0:
        raise ValidationError("Montant invalide")

    # 1️⃣ Débit balance (peut lever ValueError si solde insuffisant)
    BalanceService.debit(user, amount, currency)

    # 2️⃣ Ledger
    tx = Transaction.objects.create(
        user=user,
        amount=amount,
        currency=currency,
        transaction_type=Transaction.DEBIT,
        source=source,
        status=Transaction.STATUS_COMPLETED,
        metadata=metadata or {},
        description=description or f"{currency.upper()} soti sou kont ou.",
    )

    return tx


# ============================================================
# TRANSFERT UTILISATEUR ➜ UTILISATEUR
# ============================================================

@db_transaction.atomic
def transfer_wallet(
    *,
    sender,
    receiver,
    amount,
    currency: str,
    metadata=None,
    description=None,
):
    """
    Transfert atomique entre deux utilisateurs
    (2 balances + 2 transactions)
    """

    if sender == receiver:
        raise ValidationError("Transfert vers soi-même interdit")

    currency = currency.lower()
    amount = Decimal(str(amount)).quantize(LEDGER_PRECISION)

    if amount <= 0:
        raise ValidationError("Montant invalide")

    # 1️⃣ Débit expéditeur
    BalanceService.debit(sender, amount, currency)

    sender_tx = Transaction.objects.create(
        user=sender,
        amount=amount,
        currency=currency,
        transaction_type=Transaction.DEBIT,
        source=Transaction.USER,
        status=Transaction.STATUS_COMPLETED,
        metadata=metadata or {},
        description=description or f"Transfert vers {receiver}",
    )

    # 2️⃣ Crédit destinataire
    BalanceService.credit(receiver, amount, currency)

    receiver_tx = Transaction.objects.create(
        user=receiver,
        amount=amount,
        currency=currency,
        transaction_type=Transaction.CREDIT,
        source=Transaction.USER,
        status=Transaction.STATUS_COMPLETED,
        metadata=metadata or {},
        description=description or f"Transfert reçu de {sender}",
    )

    return sender_tx, receiver_tx