from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db.models import Q

from notifications.services.create_notification import create_notification
from .models import Client, Employee

User = get_user_model()

# ======================================================
# 1️⃣ 👋 BIENVENUE UTILISATEUR
# ======================================================
@receiver(post_save, sender=User)
def user_welcome_notification(sender, instance, created, **kwargs):
    if not created:
        return

    create_notification(
        user=instance,
        title="👋 Byenvini",
        message="Kont ou kreye avèk siksè. Byenvini sou platfòm lan 🎉",
        notification_type="signup",
    )


# ======================================================
# 2️⃣ 🔗 ATTACHEMENT EMPLOYEE / CLIENT
# ======================================================
@receiver(post_save, sender=User)
def attach_employee_or_client(sender, instance, created, **kwargs):
    if not created:
        return

    # Employee
    employee = Employee.objects.filter(
        user__isnull=True
    ).filter(
        Q(email__iexact=instance.email) | Q(phone=instance.phone)
    ).first()

    if employee:
        employee.user = instance
        employee.save(update_fields=["user"])

    # Client
    client = Client.objects.filter(
        real_user__isnull=True
    ).filter(
        Q(email__iexact=instance.email) | Q(phone=instance.phone)
    ).first()

    if client:
        client.real_user = instance
        client.is_anonymous = False
        client.save(update_fields=["real_user", "is_anonymous"])


# ======================================================
# 3️⃣ 🤝 PARRAINAGE (LOGIQUE UNIQUEMENT)
# ======================================================
@receiver(post_save, sender=User)
def referral_logic(sender, instance, created, **kwargs):
    if not created:
        return

    if not getattr(instance, "referrer", None):
        return

    create_notification(
        user=instance.referrer,
        title="🤝 Parrainage",
        message=f"Votre filleul {instance.email} s'est inscrit avec succès 🎉",
        notification_type="referral",
    )