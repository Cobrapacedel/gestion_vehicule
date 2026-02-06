from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

from notifications.models import Notification
from contracts.models import Contract
from documents.models import Document, DocumentRenewal
from fines.models import Fine, DeletedFine
from tolls.models import TollDebt, TollDetection, TollBooth
#from notifications.services.creation_notification import creation_notification
from users.utils import send_email_safe
from payments.services.reward_service import reward_user_for_task
from vehicles.models import Vehicle, VehicleStatusHistory
from users.models import Employee, LoginAttempt
from payments.models import (
    Balance,
    Transaction,
    Payment,
    Recharge,
    FundTransfer,
    Wallet
)

User = get_user_model()

# ======================================================
# 📝 CRÉATION DE CONTRAT
# ======================================================
@receiver(post_save, sender=Contract)
def notify_contract_created(sender, instance, created, **kwargs):
    if not created:
        return

    Notification.objects.create(
        user=instance.new_user,
        title="Nouveau contrat 📄",
        message=(
            f"Un contrat de type « {instance.get_contract_type_display()} » "
            f"a été créé pour le véhicule {instance.vehicle}."
        ),
        notification_type=Notification.INFO,
        contract=instance if hasattr(Notification, "contract") else None
    )
    
    tx = reward_user_for_task(instance, "CONTRACT")

    # Email de bienvenue
    send_email_safe(
        user=instance,
        subject="Nouveau contrat 📄",
        message=(
            f"Un contrat de type « {instance.get_contract_type_display()} » "
            f"a été créé pour le véhicule {instance.vehicle}."
    ),
    )
    
# ======================================================
# 🔄 CHANGEMENT DE STATUT
# ======================================================
@receiver(pre_save, sender=Contract)
def notify_contract_status_change(sender, instance, **kwargs):
    if not instance.pk:
        return

    old = Contract.objects.filter(pk=instance.pk).first()
    if not old or old.contract_status == instance.contract_status:
        return

    status_map = {
        Contract.CONTRACT_DRAFTED: (Notification.WARNING, "Contrat en négociation ✍️"),
        Contract.CONTRACT_COMPLETED: (Notification.SUCCESS, "Contrat complété ✅"),
        Contract.CONTRACT_CANCELLED: (Notification.DANGER, "Contrat annulé ❌"),
    }

    if instance.contract_status not in status_map:
        return

    notif_type, title = status_map[instance.contract_status]

    Notification.objects.create(
        user=instance.new_user,
        title=title,
        message=(
            f"Le contrat pour le véhicule {instance.vehicle} "
            f"est maintenant : {instance.get_contract_status_display()}."
        ),
        notification_type=notif_type,
        contract=instance if hasattr(Notification, "contract") else None
    )

# ======================================================
# 💳 CONTRAT PAYÉ
# ======================================================
@receiver(pre_save, sender=Contract)
def notify_contract_paid(sender, instance, **kwargs):
    if not instance.pk:
        return

    old = Contract.objects.filter(pk=instance.pk).first()
    if not old:
        return

    if not old.is_paid and instance.is_paid:
        Notification.objects.create(
            user=instance.new_user,
            title="Paiement du contrat reçu 💳",
            message=(
                f"Le paiement du contrat pour le véhicule {instance.vehicle} "
                f"a été effectué avec succès."
            ),
            notification_type=Notification.SUCCESS,
            contract=instance if hasattr(Notification, "contract") else None
        )


# ======================================================
# ⏰ LOCATION EN RETARD
# ======================================================
@receiver(post_save, sender=Contract)
def notify_rent_overdue(sender, instance, created, **kwargs):
    if instance.contract_type != Contract.CONTRACT_RENTED:
        return

    if instance.return_date:
        return

    if not instance.end_date:
        return

    today = timezone.now().date()

    if today <= instance.end_date:
        return

    Notification.objects.create(
        user=instance.new_user,
        title="Location en retard ⏰",
        message=(
            f"La location du véhicule {instance.vehicle} "
            f"a dépassé la date prévue ({instance.end_date}). "
            f"Des pénalités peuvent s’appliquer."
        ),
        notification_type=Notification.WARNING,
        contract=instance if hasattr(Notification, "contract") else None
    )


# ======================================================
# 💸 PÉNALITÉ DE LOCATION
# ======================================================
@receiver(post_save, sender=Contract)
def notify_rent_penalty(sender, instance, created, **kwargs):
    if instance.contract_type != Contract.CONTRACT_RENTED:
        return

    if instance.penalty_amount and instance.penalty_amount > 0:
        Notification.objects.create(
            user=instance.new_user,
            title="Pénalité de retard 💸",
            message=(
                f"Une pénalité de {instance.penalty_amount} a été appliquée "
                f"pour le retard du véhicule {instance.vehicle}."
            ),
            notification_type=Notification.ALERT,
            contract=instance if hasattr(Notification, "contract") else None
        )

# ======================================================
# 📄 NOUVEAU DOCUMENT AJOUTÉ
# ======================================================
@receiver(post_save, sender=Document)
def notify_document_created(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.mandatory:
        Notification.objects.create(
            user=instance.user,
            title="Document obligatoire ajouté",
            message=(
                f"Le document {instance.get_document_type_display()} "
                "a été ajouté et est requis."
            ),
            notification_type=Notification.ALERT,
            document=instance
        )


# ======================================================
# ⏰ DOCUMENT PROCHE DE L’EXPIRATION
# ======================================================
@receiver(post_save, sender=Document)
def notify_document_expiry(sender, instance, created, **kwargs):
    if not instance.expiry_date or not instance.is_valid:
        return

    today = timezone.now().date()
    days_left = (instance.expiry_date - today).days

    # Rappel à 30 jours
    if days_left == 30:
        Notification.objects.create(
            user=instance.user,
            title="Document bientôt expiré ⏳",
            message=(
                f"Votre {instance.get_document_type_display()} "
                "expire dans 30 jours."
            ),
            notification_type=Notification.REMIND,
            document=instance
        )

    # Expiré
    if days_left < 0:
        Notification.objects.create(
            user=instance.user,
            title="Document expiré ⚠️",
            message=(
                f"Votre {instance.get_document_type_display()} "
                "a expiré. Veuillez le renouveler."
            ),
            notification_type=Notification.DANGER,
            document=instance
        )


# ======================================================
# 🔄 RENOUVELLEMENT DE DOCUMENT
# ======================================================
@receiver(post_save, sender=DocumentRenewal)
def notify_document_renewed(sender, instance, created, **kwargs):
    if not created:
        return

    Notification.objects.create(
        user=instance.document.user,
        title="Document renouvelé ✅",
        message=(
            f"Votre document {instance.document.get_document_type_display()} "
            f"a été renouvelé jusqu’au {instance.new_expiry}."
        ),
        notification_type=Notification.SUCCESS,
        document=instance
    )


# ======================================================
# 💳 RENOUVELLEMENT PAYÉ
# ======================================================
@receiver(post_save, sender=DocumentRenewal)
def notify_document_renewal_paid(sender, instance, created, **kwargs):
    if not instance.is_paid:
        return

    Notification.objects.create(
        user=instance.document.user,
        title="Renouvellement payé 💳",
        message=(
            f"Le renouvellement de votre "
            f"{instance.document.get_document_type_display()} "
            "a été payé avec succès."
        ),
        notification_type=Notification.SUCCESS,
        document=instance
    )

# ======================================================
# 🚨 NOUVELLE CONTRAVENTION
# ======================================================
@receiver(post_save, sender=Fine)
def notify_fine_created(sender, instance, created, **kwargs):
    if not created:
        return

    Notification.objects.create(
        user=instance.owner,
        title="Nouvelle contravention 🚨",
        message=(
            f"Une contravention ({instance.fine_id}) a été émise pour "
            f"{instance.violation.reason}. "
            f"Montant : {instance.violation.amount} {instance.currency}. "
            f"Échéance : {instance.due_date}."
        ),
        notification_type=Notification.DANGER,
        fine=instance
    )


# ======================================================
# 💳 CONTRAVENTION PAYÉE
# ======================================================
@receiver(post_save, sender=Fine)
def notify_fine_paid(sender, instance, created, **kwargs):
    if not instance.is_paid:
        return

    Notification.objects.create(
        user=instance.owner,
        title="Contravention payée ✅",
        message=(
            f"La contravention {instance.fine_id} a été réglée avec succès. "
            "Merci pour votre paiement."
        ),
        notification_type=Notification.SUCCESS,
        fine=instance
    )

# ======================================================
# ⚠️ PÉNALITÉ APPLIQUÉE (RETARD)
# ======================================================
@receiver(post_save, sender=Fine)
def notify_fine_penalty(sender, instance, created, **kwargs):
    if instance.is_paid:
        return

    if not instance.due_date:
        return

    today = timezone.now().date()

    if today <= instance.due_date:
        return

    # éviter doublon
    if instance.penalty_applied_at:
        return

    Notification.objects.create(
        user=instance.owner,
        title="Pénalité appliquée ⚠️",
        message=(
            f"La contravention {instance.fine_id} est en retard. "
            f"Nouveau montant avec pénalité : "
            f"{instance.amount_with_penalty} {instance.currency}."
        ),
        notification_type=Notification.WARNING,
        fine=instance
    )

    instance.penalty_applied_at = timezone.now()
    instance.save(update_fields=["penalty_applied_at"])

# ======================================================
# 🗑️ CONTRAVENTION SUPPRIMÉE / ARCHIVÉE
# ======================================================
@receiver(post_save, sender=DeletedFine)
def notify_fine_deleted(sender, instance, created, **kwargs):
    if not created or not instance.owner:
        return

    Notification.objects.create(
        user=instance.owner,
        title="Contravention supprimée 🗑️",
        message=(
            f"La contravention #{instance.original_id} a été supprimée. "
            f"Motif : {instance.delete_reason}."
        ),
        notification_type=Notification.INFO
    )

# =====================================================
# 🚧 DETTE DE PÉAGE — CRÉATION
# =====================================================
@receiver(post_save, sender=TollDebt)
def notify_toll_debt_created(sender, instance, created, **kwargs):
    if not created:
        return

    booth = instance.booth
    toll = booth.toll
    vehicle = booth.vehicle

    driver = instance.driver
    owner = vehicle.owner if vehicle else None

    amount = instance.amount_due
    currency = booth.currency.upper()

    # 🔔 Chauffeur — dette directe
    create_notification(
        user=driver,
        title="Nouvelle dette de péage",
        message=(
            f"Une dette de {amount} {currency} a été enregistrée "
            f"pour le péage {toll.name}."
        ),
        notification_type=Notification.INFO
    )

    # 📩 Propriétaire — information
    if owner and owner != driver:
        create_notification(
            user=owner,
            title="Information péage",
            message=(
                f"Votre véhicule a été utilisé au péage {toll.name}. "
                f"La dette est à la charge du chauffeur."
            ),
            notification_type=Notification.ALERT
        )

# =====================================================
# 🚧 DETTE DE PÉAGE — RÈGLEMENT COMPLET
# =====================================================
@receiver(post_save, sender=TollDebt)
def notify_toll_debt_paid(sender, instance, created, **kwargs):
    if created:
        return

    if not instance.is_fully_paid:
        return

    booth = instance.booth
    toll = booth.toll
    vehicle = booth.vehicle

    driver = instance.driver
    owner = vehicle.owner if vehicle else None

    # ✅ Chauffeur
    create_notification(
        user=driver,
        title="Dette de péage réglée",
        message=(
            f"Votre dette liée au péage {toll.name} "
            f"a été entièrement réglée."
        ),
        notification_type=Notification.SUCCESS
    )

    # 📩 Propriétaire
    if owner and owner != driver:
        create_notification(
            user=owner,
            title="Dette de péage réglée",
            message=(
                f"La dette de péage associée à votre véhicule "
                f"au poste {toll.name} a été réglée."
            ),
            notification_type=Notification.INFO
        )

# =====================================================
# 📸 DÉTECTION AUTOMATIQUE NON TRAITÉE
# =====================================================
@receiver(post_save, sender=TollDetection)
def notify_toll_detection(sender, instance, created, **kwargs):
    if not created:
        return

    booth = instance.booth
    toll = booth.toll
    vehicle = instance.vehicle

    if not vehicle:
        return

    owner = vehicle.owner

    create_notification(
        user=owner,
        title="Passage détecté au péage",
        message=(
            f"Un passage a été détecté au péage {toll.name}. "
            f"Le traitement est en cours."
        ),
        notification_type=Notification.ALERT
    )
    
# ======================================================
# 🆕 INSCRIPTION UTILISATEUR
# ======================================================
@receiver(post_save, sender=User)
def notify_user_signup(sender, instance, created, **kwargs):
    if not created:
        return

    # Notification bienvenue
    Notification.objects.create(
        user=instance,
        title="Byenvini 🎉",
        message="Byenvini sou platfòm nou an.",
        notification_type=Notification.SIGNUP
    )

    # Bonus inscription
    tx = reward_user_for_task(instance, "SIGNUP")

    # Email de bienvenue
    send_email_safe(
        user=instance,
        subject="Byenvini 🎉",
        message=f"Byenvini sou platfòm nou an."
    )

    # Parrainage
    if instance.referred_by:
        Notification.objects.create(
            user=instance.referred_by,
            title="Parenn 👥",
            message=f"felisitasyon, {instance.email} enskri gras ak kòd envitasyon ou an.",
            notification_type=Notification.REFERRAL
        )

        tx_referral = reward_user_for_task(instance.referred_by, "REFERRAL_SIGNUP")

        send_email_safe(
            user=instance.referred_by,
            subject="Parenn 👥",
            message=f"Vous recevez {tx_referral.amount} {tx_referral.currency} pour votre parrainage."
        )
# ======================================================
# ✅ EMAIL / PHONE VÉRIFIÉ
# ======================================================
@receiver(post_save, sender=User)
def notify_user_verification(sender, instance, created, **kwargs):
    if created:
        return

    update_fields = kwargs.get("update_fields") or []

    if "email_verified" in update_fields and instance.email_verified:
        Notification.objects.create(
            user=instance,
            title="Email vérifié ✅",
            message="Votre adresse email a été vérifiée avec succès.",
            notification_type=Notification.SUCCESS
        )

    if "phone_verified" in update_fields and instance.phone_verified:
        Notification.objects.create(
            user=instance,
            title="Téléphone vérifié ✅",
            message="Votre numéro de téléphone a été vérifié.",
            notification_type=Notification.SUCCESS
        )


# ======================================================
# 👨‍💼 NOUVEL EMPLOYÉ AJOUTÉ
# ======================================================
@receiver(post_save, sender=Employee)
def notify_employee_added(sender, instance, created, **kwargs):
    if not created:
        return

    owner = instance.business.user

    Notification.objects.create(
        user=owner,
        title="Nouvel employé ajouté",
        message=(
            f"{instance.first_name} {instance.last_name} "
            f"a été ajouté comme {instance.position} au {instance.get_employee_type_display()}."
        ),
        notification_type=Notification.INFO
    )
            # Email optionnel
# Envoi à un utilisateur
    send_email_safe(user=instance, subject="Nouvel Employé Ajouté", message=f"{instance.first_name} {instance.last_name} "
            f"a été ajouté comme {instance.position} au {instance.get_employee_type_display()}.",
)


# ======================================================
# 🔐 COMPTE VERROUILLÉ (LOGIN FAIL)
# ======================================================
@receiver(post_save, sender=LoginAttempt)
def notify_account_locked(sender, instance, created, **kwargs):
    if not instance.locked_until:
        return

    if instance.locked_until > timezone.now():
        Notification.objects.create(
            user=instance.user,
            title="Compte temporairement verrouillé 🚫",
            message="Plusieurs tentatives de connexion ont échoué. "
                    "Votre compte est temporairement bloqué.",
            notification_type=Notification.DANGER
        )

# ======================================================
# 💰 TRANSACTION TERMINÉE
# ======================================================
@receiver(post_save, sender=Transaction)
def notify_transaction_completed(sender, instance, created, **kwargs):
    if instance.status != Transaction.STATUS_COMPLETED:
        return

    notif_type = Notification.SUCCESS if instance.transaction_type == Transaction.CREDIT else Notification.WARNING

    Notification.objects.create(
        user=instance.user,
        title="💳 Tranzaksyon",
        message=(
            f" Nou {instance.get_transaction_type_display()} sou kont ou, "
            f"{instance.amount} {instance.currency}."
        ),
        notification_type=notif_type,
        transaction=instance
    )


# ======================================================
# 💳 PAIEMENT
# ======================================================
@receiver(post_save, sender=Payment)
def notify_payment(sender, instance, created, **kwargs):
    if instance.status == Payment.STATUS_COMPLETED:
        Notification.objects.create(
            user=instance.user,
            title="Paiement réussi ✅",
            message=f"Votre paiement de {instance.amount} {instance.currency} a été confirmé.",
            notification_type=Notification.SUCCESS,
            transaction=instance.transaction
        )

    elif instance.status == Payment.STATUS_FAILED:
        Notification.objects.create(
            user=instance.user,
            title="Paiement échoué ❌",
            message=f"Votre paiement de {instance.amount} {instance.currency} a échoué.",
            notification_type=Notification.DANGER
        )


# ======================================================
# 🔋 RECHARGE
# ======================================================
@receiver(post_save, sender=Recharge)
def notify_recharge(sender, instance, created, **kwargs):
    if instance.status != Recharge.STATUS_SUCCESS:
        return

    Notification.objects.create(
        user=instance.user,
        title="Recharge réussie 🔋",
        message=f"Votre compte a été rechargé de {instance.amount} {instance.currency}.",
        notification_type=Notification.SUCCESS,
        transaction=instance.transaction
    )


# ======================================================
# 🔄 TRANSFERT DE FONDS
# ======================================================
@receiver(post_save, sender=FundTransfer)
def notify_fund_transfer(sender, instance, created, **kwargs):
    if instance.status != FundTransfer.STATUS_COMPLETED:
        return

    # Expéditeur
    Notification.objects.create(
        user=instance.sender,
        title="Transfert envoyé",
        message=(
            f"Vous avez envoyé {instance.amount} {instance.currency} "
            f"à {instance.receiver.email}."
        ),
        notification_type=Notification.WARNING,
        transaction=instance.sender_transaction
    )

    # Destinataire
    Notification.objects.create(
        user=instance.receiver,
        title="Fonds reçus 🎉",
        message=(
            f"Vous avez reçu {instance.amount} {instance.currency} "
            f"de {instance.sender.email}."
        ),
        notification_type=Notification.SUCCESS,
        transaction=instance.receiver_transaction
    )


# ======================================================
# 🔐 WALLET VÉRIFIÉ
# ======================================================
@receiver(post_save, sender=Wallet)
def notify_wallet_verified(sender, instance, created, **kwargs):
    if not instance.is_verified:
        return

    Notification.objects.create(
        user=instance.user,
        title="Wallet vérifié 🔐",
        message=f"Votre wallet {instance.network.upper()} a été vérifié avec succès.",
        notification_type=Notification.SUCCESS
    )
    
# =====================================================
# 🚗 CHANGEMENT DE STATUT DU VÉHICULE
# =====================================================
@receiver(post_save, sender=VehicleStatusHistory)
def notify_vehicle_status_change(sender, instance, created, **kwargs):
    if not created:
        return

    vehicle = instance.vehicle
    owner = vehicle.owner

    if not owner:
        return

    Notification.objects.create(
        user=owner,
        title="Statut du véhicule modifié",
        message=(
            f"Le statut de votre véhicule "
            f"{vehicle.plate_number} est passé de "
            f"{instance.old_status} à {instance.new_status}."
        ),
        notification_type=Notification.ALERT
    )
