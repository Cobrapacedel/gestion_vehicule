from django.db.models.signals import post_save
from django.dispatch import receiver

from payments.models import Transaction
from notifications.services.create_notification import create_notification


# ======================================================
# 💳 NOTIFICATION TRANSACTION RÉUSSIE (GÉNÉRIQUE)
# ======================================================
@receiver(post_save, sender=Transaction)
def transaction_completed_notification(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.status != Transaction.STATUS_COMPLETED:
        return

    message = (
        instance.description
        or f"Transaction de {instance.amount} {instance.currency} effectuée avec succès."
    )

    create_notification(
        user=instance.user,
        title="ℹ️ Enfo",
        message=message,
        notification_type=instance.bonus_type.lower(),
        transaction=instance,
    )