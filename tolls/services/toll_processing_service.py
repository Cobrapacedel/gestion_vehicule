from django.db import transaction
from vehicles.models import Vehicle
from payments.models import Payment
from payments.services.balance_service import debit

def process_toll_detection(detection):
    if detection.processed:
        return None

    # 1️⃣ Trouver le véhicule
    try:
        vehicle = Vehicle.objects.select_related("owner").get(
            plate_number=detection.plate_number
        )
    except Vehicle.DoesNotExist:
        raise ValueError("Véhicule inconnu")

    user = vehicle.owner
    amount = detection.booth.price  # le péage décide du prix

    with transaction.atomic():
        # 2️⃣ Déduire le solde
        debit(user, amount)

        # 3️⃣ Créer le paiement
        payment = Payment.objects.create(
            user=user,
            amount=amount,
            currency="HTG",
            payment_type="toll",
            status="completed",
            reference_id=detection.id
        )

        # 4️⃣ Marquer comme traité
        detection.processed = True
        detection.save()

        return payment