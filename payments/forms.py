from django import forms
from .models import Payment, Recharge, Transaction, FundTransfer, Wallet
from fines.models import Fine
from documents.models import DocumentRenewal
from tolls.models import Toll   


# ---------------- PAIEMENTS AMANDES ----------------
class FinePaymentForm(forms.Form):
    fine_id = forms.ModelChoiceField(
        queryset=Fine.objects.filter(is_paid=False),
        label="Amann Non Peye",
        empty_label="Chwazi yon amann"
    )

# ---------------- PAIEMENT DOCUMENT ----------------
class DocumentPaymentForm(forms.Form):
    DOCUMENT_CHOICES = [
        ('carte_grise', 'Carte Grise'),
        ('assurance', 'Assurance'),
        ('autre', 'Autre'),
    ]
    document_type = forms.ChoiceField(choices=DOCUMENT_CHOICES, label="Kalite Dokiman")
    document_id = forms.CharField(max_length=100, label="Nimewo Referans")
    amount = forms.DecimalField(max_digits=10, decimal_places=2, label="Montant")
    payment_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Dat Peman")

# ---------------- PAIEMENT PEYAJ ----------------
class TollPaymentForm(forms.Form):
    vehicle_type_choices = [
        ('car', 'Vwati'),
        ('truck', 'Kamyon'),
        ('bus', 'Otobis'),
    ]
    toll_station = forms.CharField(max_length=100, label="Non Estasyon Peye")
    toll_booth = forms.CharField(max_length=100, label="Nimewo Pòs Peyaj")
    vehicle_type = forms.ChoiceField(choices=vehicle_type_choices, label="Kalite Machin")
    amount = forms.DecimalField(max_digits=10, decimal_places=2, label="Montant Peman")
    passage_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Dat Pase")

# ---------------- WALLET ----------------
class WalletForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ('network',)
        widgets = {
            'network': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_address(self):
        key = self.cleaned_data.get('address')
        if not key or not key.startswith('0x') or len(key) != 42:
            raise forms.ValidationError("Adresse publique invalide. Elle doit commencer par '0x' et contenir 42 caractères.")
        return key

# ---------------- RECHARGE ----------------
class RechargeForm(forms.ModelForm):
    class Meta:
        model = Recharge
        fields = ['amount', 'currency', 'method']
        widgets = {
            'method': forms.Select(attrs={'class': 'form-select'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
        }

# ---------------- TRANSFERT DE FONDS ----------------
class FundTransferForm(forms.ModelForm):
    class Meta:
        model = FundTransfer
        fields = ['sender', 'amount', 'currency', 'method', 'description']
        widgets = {
            'reciever': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'method': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        sender = kwargs.pop('sender', None)
        super().__init__(*args, **kwargs)
        if sender:
            self.fields['reciever'].queryset = self.fields['reciever'].queryset.exclude(id=sender.id)
            self.initial['sender'] = sender

    def clean_reciever(self):
        reciever = self.cleaned_data.get('reciever')
        sender = self.initial.get('sender')
        if sender and reciever == sender:
            raise forms.ValidationError("Vous ne pouvez pas vous transférer des fonds à vous-même.")
        return reciever
    
# ---------------- TRANSACTION ---------------- 
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['user', 'amount', 'currency', 'status', 'description']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control'})
        }
