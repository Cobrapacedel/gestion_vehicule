import logging
from django.db import transaction
from random import randint
from django.db.models import Q

from django.contrib.auth import get_user_model

from payments.models import Balance, BalanceCurrency
from payments.services.wallet_service import create_wallet_for_user
from payments.services.reward_service import reward_user_for_task

from otp.models import OTP
from otp.utils import generate_otp

from profiles.models import SimpleProfile, BusinessProfile
from users.models import Client, Employee

logger = logging.getLogger(__name__)
User = get_user_model()


class UserOnboardingService:
    """
    Gère TOUT le processus d'initialisation d'un utilisateur.
    À appeler UNE SEULE FOIS après création du User.
    """

    DEFAULT_CURRENCIES = ["BTC", "USDT", "BTG", "HTG"]
    DEFAULT_NETWORKS = ["bsc", "eth", "btc"]

    # ===============================
    # 🚀 POINT D’ENTRÉE UNIQUE
    # ===============================
    @classmethod
    def onboard(cls, user: User):
        logger.info(f"🚀 Onboarding user {user.id} ({user.email})")

        with transaction.atomic():
            cls._ensure_phone(user)
            cls._setup_financial_system(user)
            cls._create_wallets(user)
            cls._create_profiles(user)
            cls._attach_existing_entities(user)
            cls._generate_otp(user)
            cls._reward_signup(user)
            cls._reward_referrer(user)

        logger.info(f"✅ Onboarding terminé pour {user.email}")

    # ===============================
    # 📞 PHONE AUTO
    # ===============================
    @staticmethod
    def _ensure_phone(user):
        if user.phone:
            return

        phone = f"HTG{randint(1000000, 9999999)}"
        while User.objects.filter(phone=phone).exists():
            phone = f"HTG{randint(1000000, 9999999)}"

        user.phone = phone
        user.save(update_fields=["phone"])
        logger.info(f"📞 Phone généré pour {user.email}")

    # ===============================
    # 💰 BALANCE & CURRENCIES
    # ===============================
    @classmethod
    def _setup_financial_system(cls, user):
        balance, _ = Balance.objects.get_or_create(user=user)

        for currency in cls.DEFAULT_CURRENCIES:
            BalanceCurrency.objects.get_or_create(
                balance=balance,
                currency=currency,
                defaults={"amount": 0}
            )

        logger.info(f"💰 Balance initialisée pour {user.email}")

    # ===============================
    # 🪙 WALLETS
    # ===============================
    @classmethod
    def _create_wallets(cls, user):
        for network in cls.DEFAULT_NETWORKS:
            wallet = create_wallet_for_user(user=user, network=network)
            logger.info(
                f"🪙 Wallet {network.upper()} créé pour {user.email} ({wallet.address})"
            )

    # ===============================
    # 👤 PROFILES
    # ===============================
    @staticmethod
    def _create_profiles(user):
        if user.user_type != "business":
            SimpleProfile.objects.get_or_create(user=user)

        if user.user_type == "business" and not getattr(user, "created_via_admin", False):
            BusinessProfile.objects.get_or_create(
                user=user,
                defaults={
                    "business_name": f"{user.email.split('@')[0].capitalize()} Business",
                    "address": "Adresse par défaut",
                }
            )

        logger.info(f"👤 Profiles créés pour {user.email}")

    # ===============================
    # 🔗 ATTACH CLIENT / EMPLOYEE
    # ===============================
    @staticmethod
    def _attach_existing_entities(user):
        employee = (
            Employee.objects
            .filter(user__isnull=True)
            .filter(Q(email__iexact=user.email) | Q(phone=user.phone))
            .first()
        )

        if employee:
            employee.user = user
            employee.save(update_fields=["user"])
            logger.info(f"👨‍💼 Employee attaché à {user.email}")

        client = (
            Client.objects
            .filter(real_user__isnull=True)
            .filter(Q(email__iexact=user.email) | Q(phone=user.phone))
            .first()
        )

        if client:
            client.real_user = user
            client.is_anonymous = False
            client.save(update_fields=["real_user", "is_anonymous"])
            logger.info(f"🧑 Client attaché à {user.email}")

    # ===============================
    # 🔐 OTP
    # ===============================
    @staticmethod
    def _generate_otp(user):
        OTP.objects.create(
            user=user,
            code=generate_otp()
        )
        logger.info(f"🔐 OTP généré pour {user.email}")

    # ===============================
    # 🎁 BONUS INSCRIPTION
    # ===============================
    @staticmethod
    def _reward_signup(user):
        tx = reward_user_for_task(
            user=user,
            task_code="SIGNUP",
            allow_multiple_per_day=False,
            extra_metadata={"source": "signup"}
        )

        if tx:
            logger.info(f"🎁 Bonus signup crédité → {tx.amount} {tx.currency}")

    # ===============================
    # 🤝 BONUS PARRAINAGE
    # ===============================
    @staticmethod
    def _reward_referrer(user):
        referrer = getattr(user, "referrer", None)
        if not referrer:
            return

        reward_user_for_task(
            user=referrer,
            task_code="REFERRAL_SIGNUP",
            allow_multiple_per_day=True,
            extra_metadata={
                "referred_user": user.id,
                "source": "signup"
            }
        )

        logger.info(f"🤝 Bonus parrainage accordé à {referrer.email}")