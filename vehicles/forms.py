from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Vehicle, VehicleTransfer

User = get_user_model()

class VehicleForm(forms.ModelForm):
    status = forms.ChoiceField(choices=Vehicle.STATUS_CHOICES, widget=forms.Select(attrs={"class": "form-select"}))
    
    class Meta:
        model = Vehicle
        fields = [
            "plate_number", "year", "mileage", "color", "brand", "model",
            "fuel_type", "vehicle_type", "status", "serial_number", "image", "driver_license"
        ]
        widgets = {
            "plate_number": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Numéro d'immatriculation")}),
            "serial_number": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Numéro de série")}),
            "brand": forms.Select(attrs={"class": "form-control"}),
            "model": forms.Select(attrs={"class": "form-control"}),
            "year": forms.NumberInput(attrs={"class": "form-control", "placeholder": _("Année")}),
            "color": forms.TextInput(attrs={"class": "form-control", "placeholder": _("Couleur")}),
            "mileage": forms.NumberInput(attrs={"class": "form-control", "placeholder": _("Kilométrage")}),
            "fuel_type": forms.Select(attrs={"class": "form-select"}),
            "vehicle_type": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
        labels = {
            "plate_number": _("Numéro d'immatriculation"),
            "serial_number": _("Numéro de série"),
            "brand": _("Marque"),
            "model": _("Modèle"),
            "year": _("Année"),
            "color": _("Couleur"),
            "mileage": _("Kilométrage"),
            "fuel_type": _("Type de carburant"),
            "vehicle_type": _("Type de véhicule"),
            "status": _("Statut"),
            "image": _("Image"),
            "driver_license": _("Permis de conduire"),
        }

    def clean_mileage(self):
        mileage = self.cleaned_data.get("mileage")
        if mileage is not None:
            if mileage < 0:
                raise ValidationError(_("Le kilométrage ne peut pas être négatif."))
            if mileage > 1_000_000:
                raise ValidationError(_("Le kilométrage ne peut pas dépasser 1 000 000 km."))
        return mileage

    def clean_year(self):
        year = self.cleaned_data.get("year")
        if year is not None:
            if year < 1900 or year > 2100:
                raise ValidationError(_("Veuillez entrer une année valide (entre 1900 et 2100)."))
        return year

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image:
            if image.size > 5 * 1024 * 1024:
                raise ValidationError(_("La taille de l'image ne doit pas dépasser 5 Mo."))
            if not image.content_type.startswith("image"):
                raise ValidationError(_("Veuillez télécharger un fichier image valide."))
        return image

    def clean_plate_number(self):
        plate_number = self.cleaned_data.get("plate_number")
        if not plate_number:
            raise ValidationError(_("Le numéro d'immatriculation est requis."))
        qs = Vehicle.objects.filter(plate_number=plate_number)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError(_("Ce numéro d'immatriculation est déjà utilisé."))
        return plate_number

    def clean_serial_number(self):
        serial_number = self.cleaned_data.get("serial_number")
        if not serial_number:
            raise ValidationError(_("Le numéro de série est requis."))
        qs = Vehicle.objects.filter(serial_number=serial_number)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError(_("Ce numéro de série est déjà utilisé."))
        return serial_number

    def clean_vehicle_type(self):
        vehicle_type = self.cleaned_data.get("vehicle_type")
        valid_vehicle_types = [choice[0] for choice in Vehicle.VEHICLE_TYPE_CHOICES]
        if vehicle_type not in valid_vehicle_types:
            raise ValidationError(_("Type de véhicule invalide. Veuillez choisir parmi les options disponibles."))
        return vehicle_type

    def clean_fuel_type(self):
        fuel_type = self.cleaned_data.get("fuel_type")
        valid_fuel_types = [choice[0] for choice in Vehicle.FUEL_TYPE_CHOICES]
        if fuel_type not in valid_fuel_types:
            raise ValidationError(_("Type de carburant invalide. Veuillez choisir parmi les options disponibles."))
        return fuel_type

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance

class TransferVehicleForm(forms.ModelForm):
    class Meta:
        model = VehicleTransfer
        fields = [
            "vehicle_transfer_id", "vehicle",
            "previous_owner",
            "new_owner",
            "transfer_reason",
        ]
        widgets = {
            "vehicle": forms.Select(attrs={"class": "form-select"}),
            "previous_owner": forms.Select(attrs={"class": "form-select"}),
            "new_owner": forms.Select(attrs={"class": "form-select"}),
            "transfer_reason": forms.Textarea(attrs={"rows": 3, "class": "form-control", "placeholder": _("Rezon Transfè a")}),
        }
        labels = {
            "vehicle_transfer_id": _("ID Transfè a"),
            "vehicle": _("Machin"),
            "previous_owner": _("Ansyen Pwopriyetè"),
            "new_owner": _("Nouvo Pwopriyetè"),
            "transfer_reason": _("Rezon Transfè a"),
        }

    def clean(self):
        cleaned_data = super().clean()
        previous_owner = cleaned_data.get("previous_owner")
        new_owner = cleaned_data.get("new_owner")
        vehicle = cleaned_data.get("vehicle")

        if previous_owner == new_owner:
            raise ValidationError(_("Le nouveau propriétaire doit être différent de l'ancien propriétaire."), code="same_owner")

        if vehicle and vehicle.owner != previous_owner:
            raise ValidationError(
                _("L'ancien propriétaire doit correspondre au propriétaire actuel du véhicule."),
                code="invalid_previous_owner"
            )

        return cleaned_data