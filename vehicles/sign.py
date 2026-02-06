import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from vehicles.models import Vehicle
from payments.models import Balance
from payments.services.reward_service import TASK_REWARDS, reward_user_for_task

logger = logging.getLogger(__name__)

print("🔥 VEHICLE SIGNAL LOADED 🔥")

@receiver(post_save, sender=Vehicle)
def reward_referrer_on_first_vehicle(sender, instance, created, **kwargs):
    """
    Récompense le parrain quand le filleul crée son 1er véhicule
    """
    if not created:
        return

    owner = instance.owner
    if not owner:
        return

    referrer = owner.referrer
    if not referrer:
        return

    # Vérifier si c'est le **premier véhicule**
    if owner.owned_vehicles.exclude(pk=instance.pk).exists():
        return  # pas le premier → ne rien faire

    logger.info(f"🚀 REFERRAL FIRST VEHICLE → {referrer.email} récompensé pour {owner.email}")

    with transaction.atomic():
        reward_user_for_task(
            user=referrer,
            task_code="REFERRAL_FIRST_VEHICLE",
            allow_multiple_per_day=True,
            extra_metadata={"referred_user": owner.id, "source": "first_vehicle"}
        )
        
@receiver(post_save, sender=Vehicle)
def reward_user_after_vehicle_creation(sender, instance, created, **kwargs):
    """
    Récompense BTG automatique après création d'un véhicule.
    Crédite directement la balance et crée la transaction pour l'historique.
    """
    if not created:
        logger.info("⛔ Vehicle save mais pas created → aucun reward")
        return

    owner = instance.owner
    if not owner:
        logger.error("⛔ VEHICLE OWNER IS NONE → reward non appliqué")
        return

    logger.info(f"🚀 REWARD BTG pour {owner.email} pour CREATE_VEHICLE")

    try:
        with transaction.atomic():
            # Récupère ou crée la balance
            balance, _ = Balance.objects.get_or_create(user=owner)

            # Crédit BTG directement sur la balance
            amount = TASK_REWARDS.get("CREATE_VEHICLE", 0)
            balance.credit(amount, "BTG")
            logger.info(f"✅ {amount} BTG crédité sur le solde de {owner.email}")

            # Historique transactionnel via reward_service
            reward_user_for_task(
                user=owner,
                task_code="CREATE_VEHICLE",
                allow_multiple_per_day=True
            )
            logger.info("✅ Transaction reward_user_for_task créée")

    except Exception as e:
        logger.error(f"❌ Erreur lors de la récompense BTG du véhicule : {e}")