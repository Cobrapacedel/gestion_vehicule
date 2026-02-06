from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import DocumentRenewal

@receiver(post_save, sender=DocumentRenewal)
def update_renewal_payment_status(sender, instance, **kwargs):
    """Met à jour le statut d'un renouvellement de document lorsqu'un paiement est effectué."""
    if instance.payment:
        instance.payee = True
        instance.save()