# fines/signals.py
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Fine
from .tasks import attempt_auto_payment
from payments.models import Balance, Recharge


@receiver(post_save, sender=Fine)
def handle_fine_creation(sender, instance, created, **kwargs):
    if not created or instance.is_paid:
        return

    driver = instance.driver
    owner = instance.owner
    vehicle = instance.vehicle
    amount_to_pay = Decimal(instance.amount_with_penalty)
    deduction = (amount_to_pay * Decimal("0.95")).quantize(Decimal("0.01"))

    balance, _ = Balance.objects.get_or_create(user=driver)

    # Déterminer le champ de la devise
    field = f"{instance.currency.lower()}_balance"
    current_balance = Decimal(getattr(balance, field, Decimal("0.00")))

    vehicle_info = f"{vehicle.brand} {vehicle.model} ({vehicle.plate_number})" if vehicle else "N/A"
    driver_name = f"{driver.first_name} {driver.last_name}".strip()
    owner_name = f"{owner.first_name} {owner.last_name}".strip() if owner else ""
    
    if current_balance >= amount_to_pay:
        # Paiement automatique
        balance.debit(deduction, instance.currency)
        instance.remaining_amount = (amount_to_pay - deduction).quantize(Decimal("0.01"))
        instance.is_paid = instance.remaining_amount <= Decimal("0.01")
        instance.save()

        send_mail(
            subject="Pèman otomatik kontravansyon an",
            message=(
                f"Bonjou {driver_name} ({driver.email}),\n\n"
                f"📅 Dat & Lè: {instance.violation_date.strftime('%d/%m/%Y %H:%M')}\n"
                f"👤 Ou menm (Permis: {driver.driver_license})\n"
                f"🚗 Machin: {vehicle_info}\n"
                f"⚠️ Razon: {instance.reason}\n"
                f"💰 Kantite: {amount_to_pay} {instance.currency}\n\n"
                f"✅ Kontravansyon (ID: {instance.fine_id}) te peye otomatikman.\n"
                f"Kantite dedwi : {deduction} {instance.currency} (95%).\n"
                f"Rès pou peye : {instance.remaining_amount} {instance.currency}.\n\n"
                f"Mèsi pou koperasyon ou."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[driver.email],
            fail_silently=True,
        )

        if not instance.is_paid:
            attempt_auto_payment.delay(instance.id)

    else:
        # Solde insuffisant → création de recharge
        manque = (amount_to_pay - current_balance).quantize(Decimal("0.01"))
        Recharge.objects.create(
            user=driver,
            amount=manque,
            currency=instance.currency,
            method='AutoRecharge',
            status='Pending'
        )

        send_mail(
            subject="Kontravansyon pou Peye",
            message=(
                f"Bonjou {driver_name} ({driver.email}),\n\n"
                f"📅 Dat & Lè: {instance.violation_date.strftime('%d/%m/%Y %H:%M')}\n"
                f"👤 Ou menm (Permis: {driver.driver_license})\n"
                f"🚗 Machin: {vehicle_info}\n"
                f"⚠️ Razon: {instance.reason}\n"
                f"💰 Kantite: {amount_to_pay} {instance.currency}\n\n"
                f"Ou te resevwa yon kontravansyon (ID: {instance.fine_id}).\n"
                f"Silvouplè, peye li anvan {instance.due_date.strftime('%d/%m/%Y')} pou evite penalite 3% pa mwa.\n\n"
                f"Nou kreye otomatikman yon demann rechaj pou kont ou.\n\nMèsi."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[driver.email],
            fail_silently=True,
        )

    # Email au propriétaire du véhicule
    if owner and owner.email:
        send_mail(
            subject="Notifikasyon Kontravansyon sou machin ou",
            message=(
                f"Bonjou {owner_name} ({owner.email}),\n\n"
                f"Machin ou a te resevwa yon kontravansyon.\n\n"
                f"📅 Dat & Lè: {instance.violation_date.strftime('%d/%m/%Y %H:%M')}\n"
                f"👤 Chofè: {driver_name} (Permis: {driver.driver_license})\n"
                f"🚗 Machin: {vehicle_info}\n"
                f"⚠️ Razon: {instance.reason}\n"
                f"💰 Kantite: {amount_to_pay} {instance.currency}\n\n"
                f"Mèsi pou atansyon ou."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[owner.email],
            fail_silently=True,
        )
