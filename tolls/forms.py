from django import forms
from .models import TollBooth


class TollBoothForm(forms.ModelForm):
    class Meta:
        model = TollBooth
        fields = ['toll', 'booth_number', 'location']
        widgets = {
            'toll': forms.Select(attrs={'class': 'form-select'}),
            'booth_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex. A1'}),
            'location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Emplacement du guichet'}),
        }