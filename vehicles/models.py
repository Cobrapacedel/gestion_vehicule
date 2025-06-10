from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone

User = get_user_model()

class Renter(models.Model):
    """Modèle représentant un locataire."""

    name = models.CharField(_("Nom"), max_length=100)
    phone_number = models.CharField(_("Numéro de téléphone"), max_length=15, blank=True, null=True)
    email = models.EmailField(_("Email"), blank=True, null=True)
    address = models.CharField(_("Adresse"), max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(_("Date de création"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date de mise à jour"), auto_now=True)

    class Meta:
        verbose_name = _("Locataire")
        verbose_name_plural = _("Locataires")
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
    
class Seller(models.Model):
    """Modèle représentant un vendeur."""

    name = models.CharField(_("Nom"), max_length=100)
    phone_number = models.CharField(_("Numéro de téléphone"), max_length=15, blank=True, null=True)
    email = models.EmailField(_("Email"), blank=True, null=True)
    address = models.CharField(_("Adresse"), max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(_("Date de création"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date de mise à jour"), auto_now=True)

    class Meta:
        verbose_name = _("Vendeur")
        verbose_name_plural = _("Vendeurs")
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
    
class Transferred_to(models.Model):
    """Modèle représentant un transfert de véhicule."""

    name = models.CharField(_("Nom"), max_length=100)
    phone_number = models.CharField(_("Numéro de téléphone"), max_length=15, blank=True, null=True)
    email = models.EmailField(_("Email"), blank=True, null=True)
    address = models.CharField(_("Adresse"), max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(_("Date de création"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date de mise à jour"), auto_now=True)

    class Meta:
        verbose_name = _("Transféré à")
        verbose_name_plural = _("Transféré à")
        ordering = ["-created_at"]
    def __str__(self):
        return self.name

class Mechanic(models.Model):
    """Modèle représentant un mécanicien."""

    name = models.CharField(_("Nom"), max_length=100)
    phone_number = models.CharField(_("Numéro de téléphone"), max_length=15, blank=True, null=True)
    email = models.EmailField(_("Email"), blank=True, null=True)
    address = models.CharField(_("Adresse"), max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(_("Date de création"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date de mise à jour"), auto_now=True)

    class Meta:
        verbose_name = _("Mécanicien")
        verbose_name_plural = _("Mécaniciens")
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
    
class Vehicle(models.Model):
    STATUS_CHOICES = [
        ("available", _("Disponible")),
        ("rented", _("Loué")),
        ("maintenance", _("En maintenance")),
        ("sold", _("Vendu")),
        ("transferred", _("Transféré")),
    ]

    FUEL_TYPE_CHOICES = [
        ("gasoline", _("Essence")),
        ("diesel", _("Diesel")),
        ("electric", _("Électrique")),
    ]
    VEHICLE_TYPE_CHOICES = [
        ("car", "Machin"),
        ("motorcycle", "Moto"),
        ("truck", "Kamyon"),
        ]
    vehicle_type = models.CharField(_("Type de Vehicule"), max_length=50, choices=VEHICLE_TYPE_CHOICES, default="car")
    seller = models.ForeignKey(Seller, on_delete=models.SET_NULL, null=True, blank=True, related_name="vehicles_seller", verbose_name=_("Vendeur"))
    renter = models.ForeignKey(Renter, on_delete=models.SET_NULL, null=True, blank=True, related_name="vehicles_renter", verbose_name=_("Locataire"))
    transferred_to = models.ForeignKey(Transferred_to, on_delete=models.SET_NULL, null=True, blank=True, related_name="vehicles_transferred_to", verbose_name=_("Transféré à"))
    # Ajout d'un champ pour le mécanicien
    mechanic = models.ForeignKey(Mechanic, on_delete=models.SET_NULL, null=True, blank=True, related_name="vehicles_mechanic", verbose_name=_("Mécanicien"))
    plate_number = models.CharField(_("Numéro d'immatriculation"), max_length=20, unique=True)
    serial_number = models.CharField(_("Numéro de série"), max_length=50, unique=True)
    brand = models.CharField(_("Marque"), max_length=50)
    model = models.CharField(_("Modèle"), max_length=50)
    year = models.IntegerField(_("Année"))
    color = models.CharField(_("Couleur"), max_length=30)
    mileage = models.PositiveIntegerField(_("Kilométrage"), default=0)
    fuel_type = models.CharField(_("Type de carburant"), max_length=20, choices=FUEL_TYPE_CHOICES, default="Essence")

    driver_license = models.CharField(_("Numéro de permis de conduire"), max_length=20, blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="vehicles", verbose_name=_("Propriétaire"))
    status = models.CharField(_("Statut"), max_length=20, choices=STATUS_CHOICES, default="available")

    image = models.ImageField(_("Image"), upload_to="vehicle_images/", blank=True, null=True)

    created_at = models.DateTimeField(_("Date de création"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Date de mise à jour"), auto_now=True)

    class Meta:
        verbose_name = _("Véhicule")
        verbose_name_plural = _("Véhicules")
        ordering = ["-created_at"]
        permissions = [
            ("can_transfer_vehicle", _("Peut transférer un véhicule")),
            ("can_view_vehicle_history", _("Peut voir l'historique des véhicules")),
        ]

    def clean(self):
        """Validation supplémentaire pour le kilométrage."""
        if self.pk:  # Vérification uniquement lors de la mise à jour
            old_instance = Vehicle.objects.get(pk=self.pk)
            if self.mileage < old_instance.mileage:
                raise ValidationError(_("Le kilométrage ne peut pas diminuer."))

    def transfer_to(self, new_owner, reason=_("Transfert de propriété")):
        """Méthode pour transférer un véhicule."""
        if self.owner == new_owner:
            raise ValidationError(_("Le nouveau propriétaire doit être différent de l'ancien propriétaire."))

        self.owner = new_owner
        self.status = "transferred"
        self.save()

        # Enregistrer le transfert
        VehicleTransfer.objects.create(
            vehicle=self,
            previous_owner=self.owner,
            new_owner=new_owner,
            transfer_reason=reason
        )

    def __str__(self):
        return f"{self.brand} {self.model} - {self.plate_number}"


class VehicleTransfer(models.Model):
    """Historique des transferts de véhicules."""

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="transfers", verbose_name=_("Véhicule"))
    previous_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transfers_out", verbose_name=_("Ancien propriétaire"))
    vehicle_transfer_id = models.CharField(_("ID du Transfert"), max_length=6, blank=True)
    new_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transfers_in", verbose_name=_("Nouveau propriétaire"))

    transfer_reason = models.TextField(_("Raison du transfert"), blank=True)
    transfer_date = models.DateTimeField(_("Date de transfert"), auto_now_add=True)

    class Meta:
        verbose_name = _("Transfert de véhicule")
        verbose_name_plural = _("Transferts de véhicules")
        ordering = ["-transfer_date"]

    def __str__(self):
        return f"Transfert de {self.vehicle} de {self.previous_owner} à {self.new_owner}"