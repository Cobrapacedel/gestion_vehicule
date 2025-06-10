# tolls/tasks.py
from celery import shared_task
from django.utils import timezone
from decimal import Decimal
from .models import TollDebt
from .signals import send_debt_warning


@shared_task
def apply_debt_interest_task():
    """
    Tâche Celery pour appliquer les intérêts aux dettes impayées.
    """
    debts = TollDebt.objects.filter(is_fully_paid=False)
    for debt in debts:
        delta = timezone.now() - debt.created_at
        if delta.days >= 7:
            debt.amount_due *= Decimal("1.05")
            debt.remaining_commission *= Decimal("1.05")
            debt.save()


@shared_task
def send_debt_reminders():
    """
    Tâche pour envoyer des rappels aux utilisateurs endettés.
    """
    debts = TollDebt.objects.filter(is_fully_paid=False)
    for debt in debts:
        send_debt_warning(debt.user, debt.amount_due)