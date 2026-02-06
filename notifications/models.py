from django.db import models
from django.conf import settings


class Notification(models.Model):
    # ======================================================
    # UTILISATEUR CIBLE
    # ======================================================
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    # ======================================================
    # CONTENU
    # ======================================================
    title = models.CharField(
        max_length=255,
        verbose_name="Tit"
    )
    
    message = models.TextField(
        verbose_name="Mesaj"
    )

    # ======================================================
    # TYPE LOGIQUE
    # ======================================================
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
    SIGNUP = "signup"
    PAYMENT = "payment"
    CONTRACT = "contract"
    ALERT = "alert"
    REFERRAL = "referral"
    REMINDER = "reminder"
    BONUS = "bonus"
    
    NOTIFICATION_TYPES = [
        (INFO, "Infòmasyon"),
        (SUCCESS, "Reyisi"),
        (WARNING, "Avètisman"),
        (DANGER, "Danje"),
        (SIGNUP, "Nouvo Itilizatè"),
        (PAYMENT, "Pèman"),
        (CONTRACT, "Kontra"),
        (ALERT, "Alèt"),
        (REMINDER, "Rappel"),
        (BONUS, "Bonis"),
        (REFERRAL, "Parenn"),
    ]

    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPES,
        default=ALERT
    )

    # ======================================================
    # ÉTAT
    # ======================================================
    is_read = models.BooleanField(
        default=False,
        verbose_name="Li"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Dat"
    )

    # ======================================================
    # LIENS OPTIONNELS (CONTEXTE)
    # ======================================================
    transaction = models.ForeignKey(
        "payments.Transaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications"
    )
    
    contract = models.ForeignKey(
        "contracts.Contract",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications")

    vehicle = models.ForeignKey(
        "vehicles.Vehicle",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications"
    )

    document = models.ForeignKey(
        "documents.DocumentRenewal",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications"
    )

    fine = models.ForeignKey(
        "fines.Fine",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications"
    )

    toll = models.ForeignKey(
        "tolls.Toll",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications"
    )

    # ======================================================
    # META
    # ======================================================
    class Meta:
        verbose_name = "Notifikasyon"
        verbose_name_plural = "Notifikasyon"
        ordering = ["-created_at"]

    # ======================================================
    # MÉTHODES
    # ======================================================
    def __str__(self):
        return f"{self.user.email} | {self.title}"

    def mark_as_read(self):
        """Ekri notifikasyon an tankou yo li li deja"""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=["is_read"])

    @classmethod
    def unread_count(cls, user):
        """Kantite notifikasuon ki poko li"""
        return cls.objects.filter(user=user, is_read=False).count()

    @classmethod
    def latest_for_user(cls, user, limit=5):
        """Dernières notifications"""
        return cls.objects.filter(user=user).order_by("-created_at")[:limit]