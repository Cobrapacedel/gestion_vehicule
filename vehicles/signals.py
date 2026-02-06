import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

from vehicles.models import Vehicle
from payments.services.reward_service import reward_user_for_task
from notifications.services.create_notification import create_notification

logger = logging.getLogger(__name__)

# ======================================================
# 🚗 BONUS : PREMIER VÉHICULE (PROPRIÉTAIRE)
# ======================================================
@receiver(post_save, sender=Vehicle)
def reward_first_vehicle_owner(sender, instance, created, **kwargs):
    if not created:
        return

    owner = instance.owner
    if not owner:
        return

    # ✅ Vérification : premier véhicule UNIQUEMENT
    if Vehicle.objects.filter(owner=owner).exclude(pk=instance.pk).exists():
        return

    tx = reward_user_for_task(
        user=owner,
        task_code="CREATE_FIRST_VEHICLE",
    )

    if not tx:
        return

    create_notification(
        user=owner,
        title="🚗 Premye Veyikil",
        message=f"Ou resevwa {tx.amount} {tx.currency} pou premye veyikil ou an.",
        notification_type="bonus",
        transaction=tx,
    )


# ======================================================
# 🤝 BONUS : PREMIER VÉHICULE DU FILLEUL (PARRAIN)
# ======================================================
@receiver(post_save, sender=Vehicle)
def reward_referral_first_vehicle(sender, instance, created, **kwargs):
    if not created:
        return

    owner = instance.owner
    if not owner or not owner.referrer:
        return

    # ✅ Toujours le vrai premier véhicule
    if Vehicle.objects.filter(owner=owner).exclude(pk=instance.pk).exists():
        return

    tx = reward_user_for_task(
        user=owner.referrer,
        task_code="REFERRAL_CREATE_FIRST_VEHICLE",
        allow_multiple_per_day=True,
        extra_metadata={
            "referred_user": owner.id,
            "vehicle_id": instance.id,
        },
    )

    if not tx:
        return

    create_notification(
        user=owner.referrer,
        title="🚀 Bonis Parrainage",
        message=(
            f"{owner.email} anrejistre premye veyikil li. "
            f"Ou resevwa {tx.amount} {tx.currency}."
        ),
        notification_type="referral",
        transaction=tx,
    )