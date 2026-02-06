from django.core.mail import send_mail
from django.conf import settings
from notifications.models import Notification

def create_notification(
    user,
    title: str,
    message: str,
    notification_type: str = "alert",
    transaction=None,
    fine=None,
    #payment=None,
    document=None,
    vehicle=None,
    #recharge=None,
    #fund_transfer=None,
    contract=None,
    toll=None,
    send_email: bool = True
):
    """
    Crée une notification pour un utilisateur et envoie un email optionnel.

    Args:
        user: Utilisateur destinataire.
        title: Titre de la notification.
        message: Contenu de la notification.
        notification_type: Type (bonus, alert, reminder, payment, contract, transfer, signup, referral...).
        transaction: Optionnel, objet Transaction associé.
        fine: Optionnel, objet Fine associé.
        document: Optionnel, objet DocumentRenewal associé.
        vehicle: Optionnel, objet Vehicle associé.
        send_email: Si True, envoie un email à l'utilisateur.
    """

    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        transaction=transaction,
        fine=fine,
        document=document,
        vehicle=vehicle,
        toll=toll,
        #fund_transfer=fund_transfer,
        #payment=payment,
        contract=contract,
        #recharge=recharge
    )

    # Envoi d'email optionnel
    if send_email and user.email:
        try:
            send_mail(
                subject=title,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True
            )
        except Exception as e:
            # Ici on peut logger l'erreur si nécessaire
            print(f"Erreur envoi email notification: {e}")

    return notification