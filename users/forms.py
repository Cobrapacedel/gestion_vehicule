from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator  # Correct import
from .models import CustomUser, Profile
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import ClearableFileInput
from django.utils.translation import gettext_lazy as _

class CustomClearableFileInput(ClearableFileInput):
    initial_text = _('Aktivman')
    input_text = _('Chwazi fichye')
    clear_checkbox_label = _('Retire')
    template_name = 'widgets/custom_clearable_file_input.html'  # optionnel si tu veux un HTML spécifique

class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label=_("Imèl"), 
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Mete Imèl ou", "autofocus": True})
    )
    password = forms.CharField(
        label=_("Modpas"),
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Mete Modpas ou"})
    )

class CustomUserCreationForm(forms.ModelForm):
    driver_license = forms.CharField(max_length=50, label="Nimewo Lisans", required=True)
    password1 = forms.CharField(label="Modpas", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Konfime modpas", widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['email', 'phone_number', 'first_name', 'last_name', 'driver_license']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Imèl'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'driver_license': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Libellés personnalisés (labels)
        self.fields['email'].label = "Imèl"
        self.fields['phone_number'].label = "Nimewo telefòn"
        self.fields['first_name'].label = "Non"
        self.fields['last_name'].label = "Siyati"
        self.fields['driver_license'].label = "Nimewo Lisans"
        self.fields['password1'].label = "Modpas"
        self.fields['password2'].label = "Konfime modpas"


    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Modpas yo pa menm.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

# Custom Authentication Form
class CustomAuthenticationForm(AuthenticationForm):
    """Custom form for user login."""
    username = forms.EmailField(
        label="Imèl",
        widget=forms.TextInput(attrs={"placeholder": "Imèll"}),
    )
    password = forms.CharField(
        label="Modpas",
        widget=forms.PasswordInput(attrs={"placeholder": "Modpas"}),
    )

# Profile Update Form
class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile."""
    
    phone_number = forms.CharField(
        max_length=15,
        validators=[RegexValidator(r"^\+?1?\d{9,15}$", "Numéro de téléphone invalide.")],
        widget=forms.TextInput(attrs={
            "placeholder": "Telefòn",
            "class": "w-full rounded-md border-gray-300 shadow-sm p-2"
        }),
    )

    class Meta:
        model = Profile
        fields = ("address", "phone_number", "email_notifications", "sms_notifications", "avatar")
        widgets = {
            "address": forms.Textarea(attrs={
                "placeholder": "Adrès",
                "rows": 6,
                "class": "w-full max-w-full rounded-md border-gray-300 shadow-sm p-2 resize-none",
            }),
            "email_notifications": forms.CheckboxInput(attrs={"class": "mr-2"}),
            "sms_notifications": forms.CheckboxInput(attrs={"class": "mr-2"}),
            "avatar": forms.ClearableFileInput(attrs={"class": "block w-full text-sm text-gray-500"}),
        }

