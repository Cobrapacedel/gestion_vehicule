from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

# =========================
#  CLASSE VEHICLE
# =========================
class Vehicle(models.Model):

    # =========================
    # STATUTS
    # =========================
    AVAILABLE = "available"
    RENTED = "rented"
    SOLD = "sold"
    LOANED = "loaned"

    STATUS_CHOICES = [
        (AVAILABLE, "Disponible"),
        (RENTED, "Loué"),
        (SOLD, "Vendu"),
        (LOANED, "Prêté"),
    ]

    # =========================
    # CARBURANT
    # =========================
    GASOLINE = "gasoline"
    DIESEL = "diesel"
    ELECTRIC = "electric"
    HYBRID = "hybrid"

    FUEL_TYPE_CHOICES = [
        (GASOLINE, "Essence"),
        (DIESEL, "Diesel"),
        (ELECTRIC, "Électrique"),
        (HYBRID, "Hybride"),
    ]

    # =========================
    # TYPE DE VÉHICULE
    # =========================
    CAR = "car"
    MOTORCYCLE = "motorcycle"
    TRUCK = "truck"
    BUS = "bus"

    VEHICLE_TYPE_CHOICES = [
        (CAR, "Voiture"),
        (MOTORCYCLE, "Moto"),
        (TRUCK, "Camion"),
        (BUS, "Bus"),
    ]

    # =========================
    # PROPRIÉTAIRE
    # =========================
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_vehicles"
    )

    # =========================
    # INFORMATIONS VÉHICULE
    # =========================
    vehicle_type = models.CharField(
        verbose_name="Type de véhicule",
        max_length=50,
        choices=VEHICLE_TYPE_CHOICES,
        default=CAR
    )

    plate_number = models.CharField(
        verbose_name="Numéro d'immatriculation",
        max_length=20,
        unique=True
    )

    serial_number = models.CharField(
        verbose_name="Numéro de série",
        max_length=50,
        unique=True
    )

    brand = models.CharField(
        verbose_name="Marque",
        max_length=50
    )

    model = models.CharField(
        verbose_name="Modèle",
        max_length=50
    )

    year = models.IntegerField(
        verbose_name="Année"
    )

    color = models.CharField(
        verbose_name="Couleur",
        max_length=30,
        blank=True,
        null=True
    )

    mileage = models.PositiveIntegerField(
        verbose_name="Kilométrage",
        default=0
    )

    fuel_type = models.CharField(
        verbose_name="Type de carburant",
        max_length=20,
        choices=FUEL_TYPE_CHOICES,
        default=GASOLINE
    )

    # =========================
    # ACTEURS PROFESSIONNELS
    # =========================
    dealer = models.ForeignKey(
        "users.BusinessProfile",
        on_delete=models.CASCADE,
        limit_choices_to={"business_type": "dealer"},
        related_name="dealer_vehicles",
        null=True,
        blank=True
    )

    garage = models.ForeignKey(
        "users.BusinessProfile",
        on_delete=models.CASCADE,
        limit_choices_to={"business_type": "garage"},
        related_name="garage_vehicles",
        null=True,
        blank=True
    )

    agency = models.ForeignKey(
        "users.BusinessProfile",
        on_delete=models.CASCADE,
        limit_choices_to={"business_type": "agency"},
        related_name="agency_vehicles",
        null=True,
        blank=True
    )

    status = models.CharField(
        verbose_name="Statut",
        max_length=20,
        choices=STATUS_CHOICES,
        default=AVAILABLE
    )

    image = models.ImageField(
        verbose_name="Image",
        upload_to="vehicle_images/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # =========================
    # VALIDATIONS MÉTIER
    # =========================
    def clean(self):
        super().clean()

        if self.pk:
            old = Vehicle.objects.get(pk=self.pk)
            if self.mileage < old.mileage:
                raise ValidationError(
                    {"mileage": "Le kilométrage ne peut pas diminuer."}
                )

    def __str__(self):
        return f"{self.brand} {self.model} ({self.plate_number})"


# =========================
# HISTORIQUE DES STATUTS
# =========================
class VehicleStatusHistory(models.Model):

    vehicle = models.ForeignKey(
        "vehicles.Vehicle",
        on_delete=models.CASCADE,
        related_name="status_history",
        verbose_name="Véhicule"
    )

    old_status = models.CharField(
        verbose_name="Ancien statut",
        max_length=20,
        blank=True,
        null=True
    )

    new_status = models.CharField(
        verbose_name="Nouveau statut",
        max_length=20,
        blank=True,
        null=True
    )

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Modifié par"
    )

    changed_at = models.DateTimeField(
        verbose_name="Date de modification",
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.vehicle.plate_number}: {self.old_status} → {self.new_status}"