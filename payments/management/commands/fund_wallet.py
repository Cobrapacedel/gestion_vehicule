from django.core.management.base import BaseCommand
from decimal import Decimal
from users.models import CustomUser
from payments.services.wallet_service import create_wallet_for_user
from payments.models import Transaction, BalanceCurrency


class Command(BaseCommand):
    help = "Credit wallet for testing"

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True)
        parser.add_argument("--network", required=True)
        parser.add_argument("--amount", type=Decimal, required=True)
        parser.add_argument("--currency", default="USDT")

    def handle(self, *args, **options):
        user = CustomUser.objects.get(email=options["email"])
        wallet = create_wallet_for_user(user, options["network"])

        Transaction.objects.create(
            wallet=wallet,
            amount=options["amount"],
            currency=options["currency"],
            tx_type="CREDIT",
            source="SYSTEM_TEST",
        )

        BalanceCurrency.objects.create(
            balance=wallet.balance,
            currency=options["currency"],
            amount=options["amount"],
        )

        self.stdout.write(self.style.SUCCESS(
            f"Wallet {wallet.public_key} credited with {options['amount']} {options['currency']}"
        ))