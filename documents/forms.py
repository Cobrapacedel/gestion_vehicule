from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import Document, DocumentRenewal


# ==========================
# Widgets personnalisés
# ==========================
class CustomClearableFileInput(forms.ClearableFileInput):
    initial_text = _("Aktivman")
    input_text = _("Chwazi fichye")
    clear_checkbox_label = _("Retire")
    template_name = "widgets/custom_clearable_file_input.html"


# ==========================
# Formulaire Document
# ==========================
class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["document_type", "vehicle", "file", "expiry_date", "mandatory"]
        widgets = {
            "expiry_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "file": forms.FileInput(attrs={"class": "form-control"}),
            "document_type": forms.Select(attrs={"class": "form-control"}),
            "vehicle": forms.Select(attrs={"class": "form-control"}),
            "mandatory": forms.CheckboxInput(attrs={"class": "w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"}),
        }

    def clean_expiry_date(self):
        expiry = self.cleaned_data.get("expiry_date")
        if expiry and expiry < timezone.now().date():
            raise ValidationError(_("La date d’expiration ne peut pas être dans le passé."))
        return expiry


# ==========================
# Formulaire Renouvellement
# ==========================
class DocumentRenewalForm(forms.ModelForm):
    class Meta:
        model = DocumentRenewal
        fields = ["document", "vehicle", "old_expiry", "new_expiry"]
        widgets = {
            "old_expiry": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "new_expiry": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "document": forms.Select(attrs={"class": "form-control"}),
            "vehicle": forms.Select(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned = super().clean()
        old = cleaned.get("old_expiry")
        new = cleaned.get("new_expiry")
        if old and new and new <= old:
            raise ValidationError(_("La nouvelle date doit être postérieure à l’ancienne."))
        return cleaned

