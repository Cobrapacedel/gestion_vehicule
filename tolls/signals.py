from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.utils.crypto import get_random_string
from twilio.rest import Client

from .models import Toll, TollPayment, TollTransaction, TollDebt, TollBooth
from vehicles.models import Vehicle
from payments.models import Balance


@receiver(post_save, sender=Toll)
def send_toll_notification(sender, instance, created, **kwargs):
    """
    Envoie un email et un SMS après la création d'un enregistrement de péage.
    """
    if created:
        subject = "Confirmation de paiement du péage"
        message = (
            f"Votre véhicule ({instance.vehicle.plate_number}) est passé au péage "
            f"'{instance.toll_booth.name}'. Montant : {instance.amount} HTG."
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.user.email],
            fail_silently=False,
        )

        if hasattr(instance.user, "phone_number") and instance.user.phone_number:
            send_sms_notification(instance.user, message)


def send_sms_notification(user, message):
    """
    Envoie un SMS via Twilio à l'utilisateur concerné.
    """
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message_sent = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=user.phone_number
        )
        return message_sent.sid
    except Exception as e:
        print(f"Erreur d'envoi du SMS : {e}")
        return None


def process_vehicle_detection(plate_number, booth_id):
    """
    Déclenchée lorsqu'un véhicule est détecté : crée automatiquement paiement et transaction.
    """
    try:
        vehicle = Vehicle.objects.get(plate_number=plate_number)
        user = vehicle.owner
        balance = Balance.objects.get(user=user)
        toll_booth = TollBooth.objects.get(id=booth_id)
        amount = Decimal("1000")  # Montant fixe à ajuster selon tarif

        if balance.amount >= amount:
            deducted = amount * Decimal("0.80")
            remaining = amount * Decimal("0.20")

            balance.amount -= deducted
            balance.save()

            payment = TollPayment.objects.create(
                user=user,
                toll_booth=toll_booth,
                amount=amount,
                status="success"
            )

            TollTransaction.objects.create(
                toll_payment=payment,
                reference=get_random_string(12).upper(),
                status='success'
            )

            TollDebt.objects.create(
                user=user,
                amount_due=remaining,
                remaining_commission=remaining
            )

            send_success_message(user, amount, deducted)
        else:
            TollDebt.objects.create(
                user=user,
                amount_due=amount,
                remaining_commission=amount * Decimal("0.20")
            )
            send_debt_warning(user, amount)

    except Exception as e:
        print(f"Erreur lors du traitement du véhicule : {e}")


def apply_debt_interest():
    """
    Applique une pénalité de 5% sur les dettes impayées après 7 jours.
    """
    debts = TollDebt.objects.filter(is_fully_paid=False)
    for debt in debts:
        delta = timezone.now() - debt.created_at
        if delta.days >= 7:
            debt.amount_due *= Decimal("1.05")
            debt.remaining_commission *= Decimal("1.05")
            debt.save()


def send_success_message(user, total, paid):
    message = (
        f"Votre paiement automatique de {paid} HTG a été effectué avec succès. "
        f"Montant total : {total} HTG. 20% restants à régler ultérieurement."
    )
    send_sms_notification(user, message)


def send_debt_warning(user, total):
    message = (
        f"Paiement automatique échoué pour {total} HTG. Une dette a été enregistrée "
        f"et augmentera de 5% après 7 jours si non réglée."
    )
    send_sms_notification(user, message)