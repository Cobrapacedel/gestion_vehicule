from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Fine, FinePay
from .tasks import attempt_auto_payment
from payments.models import Balance, Recharge


@receiver(post_save, sender=Fine)
def handle_fine_creation(sender, instance, created, **kwargs):
    if not created or instance.is_paid:
        return

    balance, _ = Balance.objects.get_or_create(user=instance.user)
    amount_to_pay = instance.amount_with_penalty
    deduction = (amount_to_pay * Decimal("0.95")).quantize(Decimal("0.01"))

    if balance.amount >= amount_to_pay:
        # Paiement automatique immédiat
        balance.amount -= deduction
        balance.save()

        instance.remaining_amount = amount_to_pay - deduction
        instance.is_paid = instance.remaining_amount <= Decimal("0.01")
        instance.save()

        send_mail(
            subject="Pèman otomatik kontravansyon an",
            message=(
                f"Bonjou {instance.user.email},\n\n"
                f"Kontravansyon (ID: {instance.fine_id}) te peye otomatikman.\n"
                f"Kantite dedwi : {deduction} {instance.currency} (95%).\n"
                f"Rès pou peye : {instance.remaining_amount} {instance.currency}.\n\n"
                f"Mèsi pou koperasyon ou."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.user.email],
            fail_silently=True,
        )

        if not instance.is_paid:
            attempt_auto_payment.delay(instance.id)

    else:
        # Solde insuffisant : créer une recharge automatique
        manque = amount_to_pay - balance.amount
        Recharge.objects.create(
            user=instance.user,
            amount=manque.quantize(Decimal("0.01")),
            currency=instance.currency,
            method='AutoRecharge',
            status='Pending'
        )

        send_mail(
            subject="Kontravansyon pou Peye",
            message=(
                f"Bonjou {instance.user.email},\n\n"
                f"Ou te resevwa yon kontravansyon (ID: {instance.fine_id}) de {amount_to_pay} {instance.currency}.\n"
                f"Silvouplè, peye li anvan {instance.due_date.strftime('%d/%m/%Y')} pou evite penalite 3% pa mwa.\n\n"
                f"Nou kreye otomatikman yon demann rechaj pou kont ou.\n\nMèsi."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.user.email],
            fail_silently=True,
        )


@receiver(post_save, sender=FinePay)
def send_payment_email(sender, instance, created, **kwargs):
    if created:
        fine = instance.fine
        send_mail(
            subject="Konfimasyon Pèman Kontravansyon",
            message=(
                f"Bonjou {fine.user.email},\n\n"
                f"Kontravansyon (ID: {fine.fine_id}) te peye avèk reyisit.\n"
                f"Kantite peye : {fine.amount_with_penalty} {fine.currency}.\n\n"
                f"Mèsi anpil pou kolaborasyon ou."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[fine.user.email],
            fail_silently=True,
        )
