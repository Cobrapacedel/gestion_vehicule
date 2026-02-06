from decimal import Decimal
from django.utils import timezone
from .models import Contract

def apply_rental_penalty(contract: Contract) -> None:
    """
    Applique la pénalité pour un contrat de location si la date de retour
    est dépassée ou si le contrat est en retard.
    
    Mise à jour automatique du champ `penalty_amount` du contrat.
    """
    if contract.contract_type != Contract.CONTRACT_RENT:
        return  # Pas une location, rien à faire

    if not contract.end_date:
        return  # Date de fin non définie

    # Date actuelle
    today = timezone.now().date()

    # Si retour à temps, pas de pénalité
    if contract.return_date and contract.return_date <= contract.end_date:
        contract.penalty_amount = Decimal("0.00")
        contract.save()
        return

    # Déterminer combien de jours de retard
    days_late = 0
    if contract.return_date:
        days_late = (contract.return_date - contract.end_date).days
    else:
        days_late = (today - contract.end_date).days

    if days_late <= 0:
        contract.penalty_amount = Decimal("0.00")
    else:
        per_day = contract.penalty_per_day or Decimal("0.00")
        contract.penalty_amount = (Decimal(days_late) * Decimal(per_day)).quantize(Decimal("0.01"))

    contract.save()