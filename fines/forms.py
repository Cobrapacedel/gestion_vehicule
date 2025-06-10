from django import forms
from .models import Fine, FinePay

from django import forms
from .models import Fine

class FineForm(forms.ModelForm):
    class Meta:
        model = Fine
        fields = [
            "user",
            "fine_id",
            "driver_license",
            "vehicle",
            "violation",
            "currency",
            "base_amount",
            "violation_date",
            "reason",
        ]
        widgets = {
            "violation_date": forms.DateInput(attrs={"type": "date"}),
            "reason": forms.Textarea(attrs={"rows": 3}),
        }


class FinePayForm(forms.ModelForm):
    class Meta:
        model = FinePay
        fields = ['user', 'vehicle', 'driver_license', 'amount', 'currency']
        widgets = {
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'driver_license': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Le montant doit être supérieur à zéro.")
        return amount

class FinePaymentForm(forms.Form):
    license_plate = forms.CharField(label="Immatrikilasyon", max_length=20)
    amount = forms.DecimalField(label="Montant Amann", max_digits=10, decimal_places=2)
    fine_id = forms.CharField(label="Nimewo Kontravansyon")
    payment_date = forms.DateField(label="Dat Peman", widget=forms.DateInput(attrs={'type': 'date'}))