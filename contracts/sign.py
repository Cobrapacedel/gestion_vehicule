from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Contract
from vehicles.models import Vehicle


@receiver(post_save, sender=Contract)
def update_vehicle_status_and_owner(sender, instance, created, **kwargs):
    vehicle = instance.vehicle
    if not vehicle:
        return

    contract_type = instance.contract_type
    old_user = instance.old_user
    new_user = instance.new_user

    # --- 1. Mise à jour du statut selon le type ---
    type_map = {
        "rent": "rentals",
        "service": "mechanic",
        "loan": "loan",
        "sell": "available",       # après vente, véhicule dispo pour nouvel utilisateur
        "transfer": "available",
    }

    new_status = type_map.get(contract_type, "available")

    # --- 2. Changement de propriétaire si vente ou transfert ---
    if contract_type in ["sell", "transfer"]:
        if vehicle.owner != new_user:
            vehicle.owner = new_user
            vehicle.status = "available"   # dispo chez le nouveau propriétaire

    else:
        # Sinon, juste mise à jour du statut
        vehicle.status = new_status

    vehicle.save()