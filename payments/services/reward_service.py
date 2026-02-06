import random
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from payments.models import Balance, BalanceCurrency, Transaction
from payments.services.balance_service import BalanceService

# ======================================================
# CONSTANTES
# ======================================================
JMU = "JMU"

# Récompenses aléatoires
RANDOM_REWARDS = [
    Decimal("0.000000000005"),
    Decimal("0.000000000001"),
    Decimal("0.000000000002"),
]

# Récompenses par tâche
TASK_REWARDS = {
    "SIGNUP": Decimal("0.0000000000000005"),
    "CREATE_VEHICLE": Decimal("0.00000000000000005"),
    "PAYMENT_SUCCESS": Decimal("0.000000000000000002"),
    "DAILY_LOGIN": Decimal("0.000000000000000001"),
    "REFERRAL_SIGNUP": Decimal("0.0000000000000001"),
    "REFERRAL_CREATE_VEHICLE": Decimal("0.000000000000000005"),
    "BONUS": Decimal("0.000000000000000001")
}


# ======================================================
# UTILITAIRES
# ======================================================
def _get_balance(user):
    balance, _ = Balance.objects.get_or_create(user=user)
    return balance


def _already_rewarded_today(user, reward_key):
    """
    Empêche plusieurs récompenses identiques le même jour
    """
    return Transaction.objects.filter(
        user=user,
        currency=JMU,
        metadata__reward_key=reward_key,
        created_at__date=timezone.now().date(),
        status=Transaction.STATUS_COMPLETED,
    ).exists()


# ======================================================
# 🎲 BONUS ALÉATOIRE
# ======================================================
@transaction.atomic
def reward_user_random_jmu(user, *, allow_multiple_per_day=False):
    reward_key = "RANDOM"

    if not allow_multiple_per_day and _already_rewarded_today(user, reward_key):
        return None

    amount = random.choice(RANDOM_REWARDS)
    balance = _get_balance(user)

    tx = Transaction.objects.create(
        user=user,
        amount=amount,
        currency=JMU,
        transaction_type=Transaction.CREDIT,
        bonus_type=Transaction.BONUS,
        source=Transaction.SYSTEM,
        status=Transaction.STATUS_COMPLETED,
        description="🎁 Bonis Aleyatwa",
        metadata={
            "reward_type": "random",
            "reward_key": reward_key,
        },
    )

    BalanceService.credit(user, amount, JMU)
    return tx


# ======================================================
# 🏆 BONUS PAR TÂCHE
# ======================================================
@transaction.atomic
def reward_user_for_task(
    user,
    task_code,
    *,
    allow_multiple_per_day=False,
    extra_metadata=None,
):
    if task_code not in TASK_REWARDS:
        return None

    if not allow_multiple_per_day and _already_rewarded_today(user, task_code):
        return None

    amount = TASK_REWARDS[task_code]
    balance = _get_balance(user)
    # Determination de la traduction
    TASK_LABELS = {
    "SIGNUP": "Enskripsyon",
    "CREATE_VEHICLE": "Kreyasyon Premye Veyikil",
    "PAYMENT_SUCCESS": "Pèman Reyisi",
    "DAILY_LOGIN": "Koneksyon Chak Jou",
    "REFERRAL_SIGNUP": "Enskripsyon Fiyèl",
    "REFERRAL_FIRST_VEHICLE": "Kreyasyon Premye Veyikil Fiyèl",
    "RANDOM": "Bonis Aleyatwa",
    "BONUS": "Bonis",
}

    # Détermination du type métier
    BONUS_TYPE_MAP = {
        "SIGNUP": Transaction.SIGNUP,
        "CREATE_VEHICLE": Transaction.CREATE_VEHICLE,
        "PAYMENT_SUCCESS": Transaction.PAYMENT,
        "DAILY_LOGIN": Transaction.DAILY_LOGIN,
        "REFERRAL_SIGNUP": Transaction.REFERRAL,
        "RANDOM": Transaction.RANDOM,
        "BONUS": Transaction.BONUS,
        "REFERRAL_FIRST_VEHICLE": Transaction.REFERRAL,
    }

    bonus_type = BONUS_TYPE_MAP.get(
        task_code,
        Transaction.BONUS
    )

    label = TASK_LABELS.get(task_code, task_code)

    metadata = {
        "reward_type": "task",
        "task": task_code,
        "label": label,
    }

    if extra_metadata:
        metadata.update(extra_metadata)

    tx = Transaction.objects.create(
        user=user,
        amount=amount,
        currency=JMU,
        transaction_type=Transaction.CREDIT,
        bonus_type=Transaction.BONUS,
        source=Transaction.SYSTEM,
        status=Transaction.STATUS_COMPLETED,
        description=f"Rekonpans pou : {label} ou an",
        metadata=metadata,
    )

    BalanceService.credit(user, amount, JMU)
    return tx


# ======================================================
# 🛠️ BONUS MANUEL (ADMIN / SYSTÈME)
# ======================================================
@transaction.atomic
def reward_user_manual(
    user,
    amount,
    reason,
    *,
    source=Transaction.ADMIN,
    metadata=None,
):
    amount = Decimal(amount)
    balance = _get_balance(user)

    tx = Transaction.objects.create(
        user=user,
        amount=amount,
        currency=JMU,
        transaction_type=Transaction.CREDIT,
        bonus_type=Transaction.BONUS,
        source=source,
        status=Transaction.STATUS_COMPLETED,
        description=reason,
        metadata=metadata or {
            "reward_type": "manual"
        },
    )

    BalanceService.credit(user, amount, JMU)
    return tx