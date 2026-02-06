from django.db.models.signals import post_save
from django.dispatch import receiver

from tolls.models import Toll
from notifications.services.create_notification import create_notification


# ======================================================
# 🛣️ CRÉATION D’UN PÉAGE
# ======================================================
@receiver(post_save, sender=Toll)
def toll_created_notification(sender, instance, created, **kwargs):
    if not created:
        return

    if not instance.creator:
        return

    create_notification(
        user=instance.creator,
        title="🛣️ Nouveau péage créé",
        message=(
            f"Le péage '{instance.name}' a été ajouté "
            f"pour la route {instance.route}."
        ),
        notification_type="info",
        toll=instance,
        unique_key=f"toll_created_{instance.id}",
    )