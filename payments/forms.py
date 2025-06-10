from django import forms
from .models import Payment, Recharge, Transaction, FundTransfer, Wallet

class FinePaymentForm(forms.Form):
    license_plate = forms.CharField(label="Immatrikilasyon", max_length=20)
    amount = forms.DecimalField(label="Montant Amann", max_digits=10, decimal_places=2)
    fine_id = forms.CharField(label="Nimewo Kontravansyon")
    payment_date = forms.DateField(label="Dat Peman", widget=forms.DateInput(attrs={'type': 'date'}))


class DocumentPaymentForm(forms.Form):
    document_type = forms.ChoiceField(
        label="Kalite Dokiman",
        choices=[('carte_grise', 'Carte Grise'), ('assurance', 'Assurance'), ('autre', 'Autre')]
    )
    reference_number = forms.CharField(label="Nimewo Referans", max_length=100)
    amount = forms.DecimalField(label="Montant", max_digits=10, decimal_places=2)
    payment_date = forms.DateField(label="Dat Peman", widget=forms.DateInput(attrs={'type': 'date'}))


class TollPaymentForm(forms.Form):
    toll_station = forms.CharField(label="Non Estasyon Peye", max_length=100)
    toll_booth = forms.CharField(label="Nimewo Pòs Peyaj", max_length=100)
    vehicle_type = forms.ChoiceField(
        label="Kalite Machin",
        choices=[('car', 'Vwati'), ('truck', 'Kamyon'), ('bus', 'Otobis')]
    )
    amount = forms.DecimalField(label="Montant Peman", max_digits=10, decimal_places=2)
    passage_date = forms.DateField(label="Dat Pase", widget=forms.DateInput(attrs={'type': 'date'}))


class WalletForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ['public_key', 'network']
        widgets = {
            'network': forms.Select(attrs={'class': 'form-select'}),
            'public_key': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '0x...'}),
        }

    def clean_public_key(self):
        key = self.cleaned_data.get('public_key')
        if not key or not key.startswith('0x') or len(key) != 42:
            raise forms.ValidationError("Adresse publique invalide. Elle doit commencer par '0x' et contenir 42 caractères.")
        return key

class RechargeForm(forms.ModelForm):
    currency = forms.ChoiceField(
        choices=[
            ("HTG", "Haitian Gourde (HTG)"),
            ("USD", "US Dollar (USD)"),
            ("BTG", "Bitcoin Gold (BTG)"),
            ("BTC", "Bitcoin (BTC)"),
            ("USDT", "Tether (USDT)"),
        ],
        label="Devise",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    amount = forms.DecimalField(
        min_value=0.01,
        label="Montant",
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Montant de la recharge"
        })
    )

    class Meta:
        model = Recharge
        fields = ['amount', 'currency', 'method']
        widgets = {
            'method': forms.TextInput(attrs={"class": "form-control", "placeholder": "Méthode de paiement"})
        }


class PaymentForm(forms.ModelForm):
    amount = forms.DecimalField(
        min_value=0.01,
        label="Montant",
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Montant du paiement"
        })
    )

    class Meta:
        model = Payment
        fields = ["amount", "currency", "payment_type"]
        widgets = {
            "currency": forms.Select(attrs={"class": "form-control"}),
            "payment_type": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Type de paiement"
            }),
        }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['user', 'amount', 'currency', 'description', 'status']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Kantite'
            }),
            'currency': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Description'
            }),
            'status': forms.Select(attrs={'class': 'form-control'})
        }

class FundTransferForm(forms.ModelForm):
    class Meta:
        model = FundTransfer
        fields = ['fund_transfer_id', 'recipient', 'amount', 'currency', 'description', 'status']
        labels = {
            'fund_transfer_id': 'Nimewo Transfè',
            'recipient': "Destinatè",
            'amount': "Kantite",
            'currency': "Deviz",
            'description': "Deskripsyon",
            'status': "Estati"
        }
        widgets = {
            'fund_transfer_id': forms.TextInput(attrs={'class': 'form-control'}),
            'recipient': forms.Select(attrs={"class": "form-control"}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Kantite Lajan'
            }),
             'currency': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Rezon'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        sender = kwargs.pop('sender', None)
        super().__init__(*args, **kwargs)
        if sender:
            self.fields['recipient'].queryset = self.fields['recipient'].queryset.exclude(id=sender.id)
            self.initial['sender'] = sender  # Pour pouvoir accéder au sender dans clean_recipient

    def clean_recipient(self):
        recipient = self.cleaned_data.get('recipient')
        sender = self.initial.get('sender')
        if sender and recipient == sender:
            raise forms.ValidationError("Vous ne pouvez pas vous transférer des fonds à vous-même.")
        return recipient