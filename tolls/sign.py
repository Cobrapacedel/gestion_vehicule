from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.utils.crypto import get_random_string
from twilio.rest import Client

from .models import Toll, TollDebt, TollBooth
from vehicles.models import Vehicle
from payments.models import Balance


@receiver(post_save, sender=Toll)
def send_toll_notification(sender, instance, created, **kwargs):
    """
    Envoie un email ou SMS après la création d'un péage, seulement si nécessaire.
    Ici, pas d'utilisateur associé, donc seulement un log ou autre action.
    """
    if created:
        # Exemple : on peut juste envoyer un email à l'admin
        subject = "Nouveau péage enregistré"
        message = f"Péage ID: {instance.toll_id}, Montant : {instance.amount} HTG."

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],  # email admin
            fail_silently=False,
        )

        # Si tu as un téléphone d'alerte ou API SMS côté admin
        # send_sms_notification(admin_phone, message)


def send_sms_notification(user, message):
    """
    Envoie un SMS via Twilio à l'utilisateur concerné.
    """
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message_sent = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=user.phone
        )
        return message_sent.sid
    except Exception as e:
        print(f"Erreur d'envoi du SMS : {e}")
        return None

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