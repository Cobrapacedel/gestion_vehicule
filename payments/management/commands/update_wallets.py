from django.core.management.base import BaseCommand
from payments.models import Wallet
from payments.services.blockchain_utils import get_bnb_balance

class Command(BaseCommand):
    help = 'Met à jour les soldes de tous les wallets sur BSC'

    def handle(self, *args, **kwargs):
        bsc_wallets = Wallet.objects.filter(network='bsc')
        for wallet in bsc_wallets:
            try:
                new_balance = get_bnb_balance(wallet.public_key)
                wallet.wallet_balance = new_balance
                wallet.save()
                self.stdout.write(self.style.SUCCESS(f"{wallet.user.email} : {new_balance} BNB"))
            except Exception as e:
                self.stderr.write(f"Erreur {wallet.public_key} : {e}")