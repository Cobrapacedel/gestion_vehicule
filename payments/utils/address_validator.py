from django.core.exceptions import ValidationError


def validate_address(address: str, network: str):
    if not address:
        raise ValidationError("Adresse vide")

    address = address.strip()
    network = network.upper()

    if network in ("ETH", "BSC"):
        if not (address.startswith("0x") and len(address) == 42):
            raise ValidationError("Adresse invalide pour Ethereum / BSC")

    elif network == "BTC":
        if not address.startswith(("1", "3", "bc1")):
            raise ValidationError("Adresse invalide pour Bitcoin")

    elif network == "TRON":
        if not address.startswith("T"):
            raise ValidationError("Adresse invalide pour TRON")

    else:
        raise ValidationError("Réseau inconnu")