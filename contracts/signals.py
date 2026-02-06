from django.db.models.signals import post_save
from django.dispatch import receiver

from contracts.models import Contract
from notifications.services.create_notification import create_notification


# ======================================================
# 📄 CRÉATION DE CONTRAT
# ======================================================
@receiver(post_save, sender=Contract)
def contract_created_notification(sender, instance, created, **kwargs):
    if not created:
        return

    titles = {
        Contract.CONTRACT_SELL: "🚗 Vente de véhicule",
        Contract.CONTRACT_RENT: "📄 Location de véhicule",
        Contract.CONTRACT_LOAN: "🤝 Prêt de véhicule",
    }

    create_notification(
        user=instance.old_user,
        title=titles.get(instance.contract_type, "📄 Nouveau contrat"),
        message=(
            f"Contrat {instance.get_contract_type_display()} "
            f"créé pour le véhicule {instance.vehicle}."
        ),
        notification_type="contract",
        vehicle=instance.vehicle,
        contract=instance,
    )