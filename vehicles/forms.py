from django import forms
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from .models import (
    Vehicle, VehicleStatusHistory
)


# ============================
# FORMULAIRE VÉHICULE
# ============================
class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        exclude = ("owner",)
        fields = [
            "vehicle_type", "plate_number", "serial_number", "brand", "model", "year", "color", "mileage", "fuel_type", "status", "image"
        ]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
            "vehicle_type": forms.Select(attrs={"class": "form-select"}),
            "fuel_type": forms.Select(attrs={"class": "form-select"}),
        }


# ============================
# HISTORIQUE DES STATUTS
# ============================
class VehicleStatusHistoryForm(forms.ModelForm):
    class Meta:
        model = VehicleStatusHistory
        fields = ["vehicle", "old_status", "new_status", "changed_by"]