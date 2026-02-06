from decimal import Decimal

def format_balance(value: Decimal, sci_threshold=Decimal("0.00000001"), precision=2):
    """
    Formate un solde intelligemment :
    - 0 → "0"
    - très petit → notation scientifique (5.00E-16)
    - normal → décimal lisible
    """
    if value is None:
        return "0"

    if value == 0:
        return "0"

    value = value.normalize()

    if abs(value) < sci_threshold:
        return f"{value:.{precision}E}"

    return format(value, "f")