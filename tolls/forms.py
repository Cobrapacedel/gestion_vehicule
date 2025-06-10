from django import forms
from .models import TollPayment


class TollPaymentForm(forms.ModelForm):
    class Meta:
        model = TollPayment
        fields = ['toll_booth', 'amount', 'currency', 'payment_method']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Exemple : filtrer les guichets selon l’utilisateur (optionnel)
        if user and not user.is_superuser:
            self.fields['toll_booth'].queryset = self.fields['toll_booth'].queryset.filter(
                toll__region__icontains="Sud"  # exemple fixe
            )

        self.fields['amount'].widget.attrs.update({'placeholder': 'Ex. 500.00'})