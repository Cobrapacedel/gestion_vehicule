from django.db import models
from django.conf import settings
from payments.models import Transaction
from vehicles.models import Vehicle
from documents.models import DocumentRenewal 
from fines.models import Fine
from tolls.models import Toll

class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    NOTIFICATION_TYPES = [
        ("payment", "Paiement"),
        ("transfer", "Transfert de véhicule"),
        ("alert", "Alerte administrative"),
        ("reminder", "Rappel"),
    ]
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default="alert")

    # Liens optionnels vers d'autres modèles
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications")
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications")
    document = models.ForeignKey(DocumentRenewal, on_delete=models.CASCADE, null=True, blank=True, related_name="documents")
    toll = models.ForeignKey(Toll, on_delete=models.CASCADE, null=True, blank=True, related_name="tolls")
    fine = models.ForeignKey(Fine, on_delete=models.CASCADE, null=True, blank=True, related_name="fines")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def mark_as_read(self):
        """Marque la notification comme lue"""
        self.is_read = True
        self.save()