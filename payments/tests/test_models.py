from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal

from payments.models import (
    Balance,
    BalanceCurrency,
    Wallet,
    Payment,
    Transaction,
    Recharge,
    FundTransfer,
)

User = get_user_model()


class BasePaymentTest(TestCase):
    """Classe de base pour factoriser les utilisateurs"""

    def setUp(self):
        self.user1 = User.objects.create_user(
            email="user1@test.com", password="test1234"
        )
        self.user2 = User.objects.create_user(
            email="user2@test.com", password="test1234"
        )


# =====================================================
# BALANCE
# =====================================================
class BalanceTest(BasePaymentTest):

    def test_balance_created(self):
        balance = Balance.objects.create(user=self.user1)
        self.assertEqual(balance.user, self.user1)

    def test_credit_balance(self):
        balance = Balance.objects.create(user=self.user1)
        balance.credit(100, "HTG")

        currency = BalanceCurrency.objects.get(balance=balance, currency="HTG")
        self.assertEqual(currency.amount, Decimal("100"))

    def test_debit_balance(self):
        balance = Balance.objects.create(user=self.user1)
        balance.credit(200, "HTG")
        balance.debit(50, "HTG")

        currency = balance.currencies.get(currency="HTG")
        self.assertEqual(currency.amount, Decimal("150"))

    def test_debit_insufficient_funds(self):
        balance = Balance.objects.create(user=self.user1)

        with self.assertRaises(ValueError):
            balance.debit(10, "HTG")


# =====================================================
# WALLET
# =====================================================
class WalletTest(BasePaymentTest):

    def test_wallet_creation(self):
        wallet = Wallet.objects.create(
            user=self.user1,
            address="0xTESTADDRESS",
            network="eth",
        )

        self.assertEqual(wallet.user, self.user1)
        self.assertEqual(wallet.network, "eth")


# =====================================================
# PAYMENT
# =====================================================
class PaymentTest(BasePaymentTest):

    def setUp(self):
        super().setUp()
        self.balance = Balance.objects.create(user=self.user1)

    def test_payment_complete(self):
        payment = Payment.objects.create(
            user=self.user1,
            amount=Decimal("100"),
            currency="HTG",
            method="mobile",
        )

        payment.complete()

        self.balance.refresh_from_db()
        currency = self.balance.currencies.get(currency="HTG")

        self.assertEqual(payment.status, "completed")
        self.assertEqual(currency.amount, Decimal("100"))
        self.assertIsNotNone(payment.transaction)

    def test_payment_fail(self):
        payment = Payment.objects.create(
            user=self.user1,
            amount=Decimal("50"),
            currency="HTG",
            method="card",
        )

        payment.fail("Carte refusée")

        self.assertEqual(payment.status, "failed")
        self.assertEqual(Transaction.objects.count(), 1)


# =====================================================
# RECHARGE
# =====================================================
class RechargeTest(BasePaymentTest):

    def setUp(self):
        super().setUp()
        Balance.objects.create(user=self.user1)

    def test_recharge_complete(self):
        payment = Payment.objects.create(
            user=self.user1,
            amount=Decimal("300"),
            currency="HTG",
            method="mobile",
        )

        recharge = Recharge.objects.create(
            user=self.user1,
            amount=Decimal("300"),
            currency="HTG",
            method="mobile",
            payment=payment,
        )

        recharge.complete()

        balance = self.user1.balance
        currency = balance.currencies.get(currency="HTG")

        self.assertEqual(recharge.status, "completed")
        self.assertEqual(currency.amount, Decimal("300"))


# =====================================================
# FUND TRANSFER
# =====================================================
class FundTransferTest(BasePaymentTest):

    def setUp(self):
        super().setUp()
        self.sender_balance = Balance.objects.create(user=self.user1)
        self.recipient_balance = Balance.objects.create(user=self.user2)

        self.sender_balance.credit(500, "HTG")

    def test_successful_transfer(self):
        payment = Payment.objects.create(
            user=self.user1,
            amount=Decimal("200"),
            currency="HTG",
            method="mobile",
        )

        transfer = FundTransfer.objects.create(
            sender=self.user1,
            recipient=self.user2,
            amount=Decimal("200"),
            currency="HTG",
            method="mobile",
            description="Test transfert",
            payment=payment,
        )

        transfer.complete()

        self.assertEqual(self.sender_balance.currencies.get(currency="HTG").amount, Decimal("300"))
        self.assertEqual(self.recipient_balance.currencies.get(currency="HTG").amount, Decimal("200"))
        self.assertEqual(payment.status, "completed")

    def test_transfer_insufficient_funds(self):
        payment = Payment.objects.create(
            user=self.user1,
            amount=Decimal("1000"),
            currency="HTG",
            method="mobile",
        )

        transfer = FundTransfer.objects.create(
            sender=self.user1,
            recipient=self.user2,
            amount=Decimal("1000"),
            currency="HTG",
            method="mobile",
            description="Fail transfert",
            payment=payment,
        )

        with self.assertRaises(ValueError):
            transfer.complete()

        payment.refresh_from_db()
        self.assertEqual(payment.status, "failed")