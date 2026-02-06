from django.db.models.signals import post_save
from django.dispatch import receiver

from documents.models import DocumentRenewal
from notifications.services.create_notification import create_notification


# ======================================================
# 📄 CRÉATION DEMANDE DE RENOUVELLEMENT
# ======================================================
@receiver(post_save, sender=DocumentRenewal)
def document_renewal_created(sender, instance, created, **kwargs):
    if not created:
        return

    create_notification(
        user=instance.user,
        title="📄 Renouvellement requis",
        message=(
            f"Le document {instance.get_document_type_display()} "
            "doit être renouvelé."
        ),
        notification_type="reminder",
        document=instance,
    )


# ======================================================
# 📦 DOCUMENT PRÊT (TRANSITION DE STATUT)
# ======================================================
@receiver(post_save, sender=DocumentRenewal)
def document_ready_notification(sender, instance, **kwargs):
    if instance.status != DocumentRenewal.STATUS_READY:
        return

    # Évite les doublons (1 notification par document)
    create_notification(
        user=instance.user,
        title="📦 Document disponible",
        message=(
            f"Votre document {instance.get_document_type_display()} "
            "est prêt."
        ),
        notification_type="alert",
        document=instance,
        unique_key=f"document_ready_{instance.id}",
    )