import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from users.services.user_onboarding_service import UserOnboardingService

logger = logging.getLogger(__name__)
User = get_user_model()


# ======================================================
# 👤 USER CREATED → ONBOARDING GLOBAL
# ======================================================
@receiver(post_save, sender=User)
def user_created(sender, instance, created, **kwargs):
    """
    Déclenché UNE SEULE FOIS à la création de l'utilisateur.
    Toute la logique est déléguée au UserOnboardingService.
    """
    if not created:
        return

    logger.info(f"🚀 Signal user_created reçu pour {instance.email}")

    UserOnboardingService.onboard(instance)