import requests
from decimal import Decimal
from django.conf import settings

def get_bsc_balance(address):
    api_key = settings.BSCSCAN_API_KEY
    url = f"https://api.bscscan.com/api?module=account&action=balance&address={address}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    if data["status"] == "1":
        balance_wei = int(data["result"])
        return Decimal(balance_wei) / Decimal(10**18)
    else:
        raise Exception(f"Erreur API BscScan: {data['message']}")