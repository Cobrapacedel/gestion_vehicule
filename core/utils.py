from decimal import Decimal
from django.db.models import Sum
from payments.models import BalanceCurrency
from payments.utils.formatting import format_balance

TAUX_HTG = {
    "usdt": Decimal("132.50"),
    "btc": Decimal("8500000"),
    "jmu": Decimal("0.001"),
}

def get_user_balances(user):
    balances_qs = (
        BalanceCurrency.objects
        .filter(balance__user=user)
        .values("currency")
        .annotate(total=Sum("amount"))
    )

    soldes = {
        "btc": Decimal("0"),
        "usdt": Decimal("0"),
        "jmu": Decimal("0"),
    }

    for b in balances_qs:
        currency = b["currency"].lower()   # ✅ NORMALISATION
        soldes[currency] = b["total"] or Decimal("0")

    solde_total_htg = sum(
        (soldes[c] * TAUX_HTG[c] for c in soldes),
        start=Decimal("0")   # ✅ START SAFE
    )

    return {
        "solde_btc": format_balance(soldes["btc"]),
        "solde_usdt": format_balance(soldes["usdt"]),
        "solde_jmu": format_balance(soldes["jmu"]),
        "solde_total_htg": format_balance(solde_total_htg),
    }