from celery import shared_task
from decimal import Decimal
from django.utils import timezone
from .models import Fine
from payments.models import Balance
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def attempt_auto_payment(fine_id):
    try:
        fine = Fine.objects.get(id=fine_id)
    except Fine.DoesNotExist:
        return

    if fine.is_paid:
        return

    balance, _ = Balance.objects.get_or_create(user=fine.user)

    while True:
        amount_due = fine.remaining_amount
        if amount_due <= Decimal('0.01'):
            fine.is_paid = True
            fine.remaining_amount = Decimal('0.00')
            fine.save()
            break

        payment_portion = (amount_due * Decimal('0.95')).quantize(Decimal('0.01'))

        if balance.amount >= payment_portion:
            balance.amount -= payment_portion
            balance.save()

            fine.remaining_amount = (amount_due - payment_portion).quantize(Decimal('0.01'))
            fine.save()

            send_mail(
                subject="Paiement partiel automatique effectué",
                message=(
                    f"Bonjour {fine.user.username},\n\n"
                    f"Nous avons déduit automatiquement 95% de votre solde pour votre contravention ID {fine.id}.\n"
                    f"Montant déduit : {payment_portion} {fine.currency}.\n"
                    f"Montant restant : {fine.remaining_amount} {fine.currency}.\n"
                    f"Merci de régler le reste pour éviter des pénalités.\n"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[fine.user.email],
                fail_silently=True,
            )
        else:
            # Solde insuffisant, on envoie notification
            send_mail(
                subject="Solde insuffisant pour paiement automatique",
                message=(
                    f"Bonjour {fine.user.username},\n\n"
                    f"Votre solde est insuffisant pour régler la contravention ID {fine.id}.\n"
                    f"Montant dû : {fine.remaining_amount} {fine.currency}.\n"
                    f"Veuillez effectuer un paiement avant le {fine.due_date.strftime('%d/%m/%Y')} pour éviter une pénalité de 3% par mois.\n"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[fine.user.email],
                fail_silently=True,
            )
            break

@shared_task
def process_fines_penalties():
    from datetime import timedelta
    from django.utils import timezone
    threshold_date = timezone.now() - timedelta(days=15)
    fines = Fine.objects.filter(is_paid=False).filter(
        models.Q(penalty_applied_at__lt=threshold_date) | models.Q(penalty_applied_at__isnull=True)
    )
    for fine in fines:
        if fine.apply_penalty():
            attempt_auto_payment.delay(fine.id)
