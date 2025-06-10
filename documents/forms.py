from django import forms from .models import DocumentRenewal, DocumentPayment

class DocumentRenewalForm(forms.ModelForm):
    amount = forms.DecimalField( min_value=0.01, label="Renewal Amount", widget=forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly"}) )

class Meta:
    model = DocumentRenewal
    fields = ["vehicle", "document_type", "amount", "currency"]
    widgets = {
        "vehicle": forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
        "document_type": forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
        "currency": forms.Select(attrs={"class": "form-control", "readonly": "readonly"}),
    }
    
class DocumentPaymentForm(forms.Form):"""
    document_type = forms.ChoiceField(
        label="Kalite Dokiman",
        choices=[('carte_grise', 'Carte Grise'), ('assurance', 'Assurance'), ('autre', 'Autre')]
    )
    reference_number = forms.CharField(label="Nimewo Referans", max_length=100)
    amount = forms.DecimalField(label="Montant", max_digits=10, decimal_places=2)
    payment_date = forms.DateField(label="Dat Peman", widget=forms.DateInput(attrs={'type': 'date'}))
    """
        class Meta:
        model = DocumentPayment
        fields = ['refe reference_number', 'amount', 'currency', 'document_type', 'status']
        labels = {
            'reference_number': 'Nimewo Dokiman',
            'amount': "Kantite",
            'currency': "Deviz",
            'document_type': "Deskripsyon",
            'status': "Estati"
        }
        widgets = {
            'reference_number': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Kantite Lajan'
            }),
             'currency': forms.Select(attrs={'class': 'form-control'}),
            'document_type': forms.Select(attrs={
                'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        
    