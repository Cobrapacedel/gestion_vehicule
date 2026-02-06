import logging
from django.db import IntegrityError, transaction
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from random import randint
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.exceptions import ValidationError
from .models import SimpleProfile, BusinessProfile
from payments.services.wallet_service import create_wallet_for_user
from payments.services.reward_service import reward_user_for_task
from otp.models import OTP
from .utils import generate_otp
from .models import Client, Employee 
from payments.models import Balance, BalanceCurrency
from notifications.models import Notification

logger = logging.getLogger(__name__)

User = get_user_model()

@receiver(post_save, sender=User)
def link_referrer(sender, instance, created, **kwargs):
    if created and instance.referred_by:
        # logique métier (reward, validation)
    
@receiver(post_save, sender=User)
def setup_user_financial_system(sender, instance, created, **kwargs):
    if not created:
        return

    logger.info(f"👤 New user created → financial setup → {instance}")

    with transaction.atomic():

        # =========================
        # BALANCE
        # =========================
        balance, _ = Balance.objects.get_or_create(user=instance)
        
        # =========================
        # SOLDES PAR DÉFAUT
        # =========================
        default_currencies = ["BTC", "USDT", "BTG", "HTG"]
        for currency in default_currencies:
            BalanceCurrency.objects.get_or_create(
                balance=balance,
                currency=currency,
                defaults={"amount": 0}
            )

        logger.info(f"💰 Balance créée pour {instance.email}")

# =========================
        # WALLETS PAR RÉSEAU
        # =========================
        default_networks = ["bsc", "eth", "btc"]
        for network in default_networks:
            wallet = create_wallet_for_user(user=instance, network=network)
            logger.info(f"🪙 Wallet {network.upper()} créé pour {instance.email} | {wallet.address}")

        # =========================
        # REWARD BTG INSCRIPTION
        # =========================
        tx = reward_user_for_task(
            user=instance,
            task_code="SIGNUP",
            allow_multiple_per_day=False,
            extra_metadata={"source": "signup"}
        )
        if tx:
            logger.info(f"🎉 BTG reward crédité après inscription pour {instance.email} | Amount: {tx.amount}")
        else:
            logger.info(f"ℹ️ Reward BTG déjà crédité aujourd’hui pour {instance.email}")
    
@receiver(m2m_changed, sender=User.extra_roles.through)
def validate_extra_roles(sender, instance, action, pk_set, **kwargs):
    if action == "pre_add":
        if instance.user_type != "simple":
            raise ValidationError(
                "Seuls les utilisateurs simples peuvent avoir des rôles métiers."
            )
            
@receiver(post_save, sender=User)
def reward_referrer_on_signup(sender, instance, created, **kwargs):
    """
    Récompense le parrain lorsque son filleul s'inscrit
    """
    if not created:
        return

    referrer = instance.referrer
    if not referrer:
        return

    logger.info(f"🎉 REFERRAL SIGNUP → {referrer.email} récompensé pour {instance.email}")

    with transaction.atomic():
        reward_user_for_task(
            user=referrer,
            task_code="REFERRAL_SIGNUP",
            allow_multiple_per_day=True,
            extra_metadata={"referred_user": instance.id, "source": "signup"}
        )

@receiver(post_save, sender=User)
def attach_existing_employee(sender, instance, created, **kwargs):
    """
    Si un Employee existe déjà (créé par un business),
    le rattacher automatiquement à l'utilisateur
    lors de l'inscription.
    """
    if not created:
        return

    employee = (
        Employee.objects
        .filter(user__isnull=True)
        .filter(
            Q(email__iexact=instance.email) |
            Q(phone=instance.phone)
        )
        .first()
    )

    if employee:
        employee.user = instance

        # Optionnel : synchroniser les noms
        if not employee.first_name:
            employee.first_name = instance.first_name or ""
        if not employee.last_name:
            employee.last_name = instance.last_name or ""

        employee.save(update_fields=[
            "user", "first_name", "last_name"
        ])
        
def fix_orphan_employees():
    for employee in Employee.objects.filter(user__isnull=True):
        user = CustomUser.objects.filter(
            Q(email__iexact=employee.email) |
            Q(phone=employee.phone)
        ).first()

        if user:
            employee.user = user
            employee.save(update_fields=["user"])

@receiver(post_save, sender=User)
def attach_existing_client(sender, instance, created, **kwargs):
    if not created:
        return

    client = (
        Client.objects
        .filter(
            real_user__isnull=True,
            created_by__isnull=False,  # sécurité
        )
        .filter(
            Q(email__iexact=instance.email) |
            Q(phone=instance.phone)
        )
        .first()
    )

    if client:
        client.real_user = instance
        client.is_anonymous = False
        client.save(update_fields=["real_user", "is_anonymous"])
        
@receiver(post_save, sender=User)
def create_user_related_objects(sender, instance, created, **kwargs):
    if not created:
        return

    # --- Phone auto ---
    if not instance.phone:
        phone = f"HTG{randint(1000000, 9999999)}"
        while User.objects.filter(phone=phone).exists():
            phone = f"HTG{randint(1000000, 9999999)}"
        instance.phone = phone
        instance.save(update_fields=["phone"])

    # --- Profiles ---
    if instance.user_type != "business":
        SimpleProfile.objects.get_or_create(user=instance)

    if instance.user_type == "business" and not getattr(instance, "created_via_admin", False):
        BusinessProfile.objects.get_or_create(
            user=instance,
            defaults={
                "business_name": f"{instance.email.split('@')[0].capitalize()} Business",
                "address": "Adresse par défaut",
            }
        )


    # --- OTP ---
    OTP.objects.create(user=instance, code=generate_otp())