import requests
from django.conf import settings

def get_bsc_wallet_balance(address):
    url = f"https://api.bscscan.com/api"
    params = {
        "module": "account",
        "action": "balance",
        "address": address,
        "apikey": settings.BSCSCAN_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()

    if data["status"] == "1":
        # Conversion de wei vers BNB
        return int(data["result"]) / 10**18
    return None