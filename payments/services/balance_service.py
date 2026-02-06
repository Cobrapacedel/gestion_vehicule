from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError

from payments.models import Balance, LEDGER_PRECISION


class BalanceService:
    """
    Service central pour gérer les soldes utilisateurs
    (basé sur BalanceCurrency)
    """

    @staticmethod
    def get_or_create_balance(user):
        balance, _ = Balance.objects.get_or_create(user=user)
        return balance

    # ==========================
    # CREDIT
    # ==========================
    @staticmethod
    @transaction.atomic
    def credit(user, amount, currency):
        amount = Decimal(str(amount)).quantize(LEDGER_PRECISION)
        if amount <= 0:
            raise ValidationError("Le montant doit être positif")

        balance = BalanceService.get_or_create_balance(user)
        balance.credit(amount, currency)

        return balance

    # ==========================
    # DEBIT
    # ==========================
    @staticmethod
    @transaction.atomic
    def debit(user, amount, currency):
        amount = Decimal(str(amount)).quantize(LEDGER_PRECISION)
        if amount <= 0:
            raise ValidationError("Le montant doit être positif")

        balance = BalanceService.get_or_create_balance(user)
        balance.debit(amount, currency)

        return balance

    # ==========================
    # CHECK
    # ==========================
    @staticmethod
    def has_sufficient_balance(user, amount, currency):
        amount = Decimal(str(amount)).quantize(LEDGER_PRECISION)
        balance = BalanceService.get_or_create_balance(user)
        bc = balance.get_currency(currency)
        return bc.amount >= amount