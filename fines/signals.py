from django.db.models.signals import post_save
from django.dispatch import receiver

from fines.models import Fine
from notifications.services.create_notification import create_notification


# ======================================================
# 🚨 CRÉATION D’UNE AMENDE
# ======================================================
@receiver(post_save, sender=Fine)
def fine_created_notification(sender, instance, created, **kwargs):
    if not created:
        return

    if not instance.driver:
        return

    create_notification(
        user=instance.driver,
        title="🚨 Nouvelle amende",
        message=(
            f"Vous avez reçu une amende de "
            f"{instance.base_amount} HTG pour {instance.violation}."
        ),
        notification_type="alert",
        fine=instance,
        unique_key=f"fine_created_{instance.id}",
    )