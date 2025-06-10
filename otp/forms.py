from django import forms
from .models import OTP

# OTP Verification Form    
class OTPVerificationForm(forms.Form):
    code = forms.CharField(
        label="",
        max_length=6,
        widget=forms.NumberInput(
            attrs={
                'placeholder': 'ex: 123456',
                'class': 'appearance-none rounded relative block w-full px-10 py-2 bg-gray-700 border border-gray-600 placeholder-gray-400 text-white focus:outline-none focus:ring-red-500 focus:border-red-500 sm:text-sm'
            }
        )
    )

    def clean_code(self):
        code = self.cleaned_data.get("code")
        if len(code) != 6:
            raise forms.ValidationError("Le code OTP doit avoir exactement 6 chiffres.")
        if not code.isdigit():
            raise forms.ValidationError("Le code OTP doit contenir uniquement des chiffres.")
        return code