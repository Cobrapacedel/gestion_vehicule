from decimal import Decimal, InvalidOperation
from django import template

register = template.Library()

@register.filter
def crypto(value, precision=18):
    try:
        if value is None:
            return "0"

        if not isinstance(value, Decimal):
            value = Decimal(str(value))

        return f"{value:.{int(precision)}f}"
    except (InvalidOperation, ValueError, TypeError):
        return "0"