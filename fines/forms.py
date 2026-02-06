from django import forms
from django.core.exceptions import ValidationError
from .models import Fine, DeletedFine, Violation
from vehicles.models import Vehicle
from users.models import CustomUser


# ============================
# Formulaire Fine
# =========================
class FineForm(forms.ModelForm):
    driver_license = forms.CharField(label="Nimewo Lisans")

    owner = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(is_active=True),
        label="Pwopriyetè",
        required=True
    )

    vehicle = forms.ModelChoiceField(
        queryset=Vehicle.objects.none(),
        label="Veyikil",
        required=True
    )

    class Meta:
        model = Fine
        fields = [
            "driver_license",
            "owner",
            "vehicle",
            "violation",
        ]
        
def clean_driver_license(self):
    license_number = self.cleaned_data.get("driver_license")

    try:
        profile = SimpleProfile.objects.get(
            driver_license_number=license_number
        )
    except SimpleProfile.DoesNotExist:
        raise ValidationError("Chofè pa egziste")

    return profile.user

# ============================
# Formulaire DeletedFine
# ============================
class DeletedFineForm(forms.ModelForm):
    delete_reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True,
        label="Raison de la suppression",
        help_text="Expliquez pourquoi cette amende est supprimée"
    )

    class Meta:
        model = DeletedFine
        fields = ['original_id', 'owner', 'deleted_by', 'delete_reason']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limiter les choix aux utilisateurs actifs
        self.fields['owner'].queryset = CustomUser.objects.filter(is_active=True)
        self.fields['deleted_by'].queryset = CustomUser.objects.filter(is_staff=True, is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('delete_reason'):
            self.add_error('delete_reason', "La raison de suppression est obligatoire.")
        return cleaned_data

# ============================
# Formulaire Violation
# ============================
class ViolationForm(forms.ModelForm):
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True,
        label="Raison de la violation"
    )

    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        min_value=0.01,
        label="Montant"
    )

    currency = forms.ChoiceField(
        choices=Violation._meta.get_field('currency').choices,
        required=True,
        label="Devise"
    )

    class Meta:
        model = Violation
        fields = ['reason', 'amount', 'currency']

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise ValidationError("Le montant doit être supérieur à zéro.")
        return amount
    
    def clean_reason(self):
        reason = self.cleaned_data.get('reason')
        if not reason.strip():
            raise ValidationError("La raison ne peut pas être vide.")
        return reason   
    
    