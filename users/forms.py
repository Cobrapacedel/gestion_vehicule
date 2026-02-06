from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

from .models import (
    CustomUser,
    SimpleProfile,
    BusinessProfile,
    Client,
    Employee,
    LoginAttempt,
    LoginHistory
)

User = get_user_model()

# =========================================================
# 1. CRÉATION UTILISATEUR
# =========================================================
class CustomUserCreationForm(forms.ModelForm):

    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label="Confirmer mot de passe",
        widget=forms.PasswordInput
    )

    class Meta:
        model = CustomUser
        fields = ["email", "phone", "password1", "password2", "role", "user_type"]
        widgets = {
            "user_type": forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        user_type = kwargs.pop("user_type", None)
        super().__init__(*args, **kwargs)

        self.fields["user_type"].required = False

        if user_type:
            self.fields["user_type"].initial = user_type

        if user_type == "simple":
            self.fields.pop("role", None)

        if user_type == "business":
            self.fields["role"].required = True

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Modpas yo pa menm.")
        return p2

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get("role")

        if role in {"dealer", "agency", "garage"}:
            cleaned["user_type"] = "business"
        else:
            cleaned["user_type"] = "simple"

        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

        return user


# =========================================================
# 2. MODIFICATION UTILISATEUR
# =========================================================
class CustomUserChangeForm(forms.ModelForm):

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = ("email", "phone", "user_type", "role", "password", "is_active", "is_staff")


# =========================================================
# 3. PROFIL UTILISATEUR SIMPLE
# =========================================================
class SimpleProfileForm(forms.ModelForm):

    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=True)

    class Meta:
        model = SimpleProfile
        fields = [
            "email", "phone",
            "first_name", "last_name",
            "address",
            "driver_license_number",
            "driver_license_image",
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields["email"].initial = self.user.email
            self.fields["phone"].initial = self.user.phone

    def save(self, commit=True):
        simple = super().save(commit=False)

        if self.user:
            self.user.email = self.cleaned_data["email"]
            self.user.phone = self.cleaned_data["phone"]
            self.user.save()
            simple.user = self.user

        if commit:
            simple.save()

        return simple


# =========================================================
# 4. PROFIL BUSINESS
# =========================================================
class BusinessProfileForm(forms.ModelForm):

    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=True)

    class Meta:
        model = BusinessProfile
        fields = [
            "email", "phone",
            "business_name",
            "address",
            "patente_number",
            "patente_image",
            "web_site",
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields["email"].initial = self.user.email
            self.fields["phone"].initial = self.user.phone

    def save(self, commit=True):
        business, _ = BusinessProfile.objects.get_or_create(user=self.user)

        for field in self.Meta.fields:
            setattr(business, field, self.cleaned_data.get(field))

        self.user.email = self.cleaned_data["email"]
        self.user.phone = self.cleaned_data["phone"]
        self.user.save()

        if commit:
            business.save()

        return business


# =========================================================
# 5. CLIENT
# =========================================================
class ClientForm(forms.ModelForm):

    real_user = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        label="Itilizatè ekziste"
    )

    class Meta:
        model = Client
        fields = [
            "real_user",
            "client_type",

            # communs
            "phone",
            "address",

            # simple
            "first_name",
            "last_name",
            "email",
            "driver_license_number",

            # business
            "business_name",
            "patente_number",
            "web_site",
        ]

    def __init__(self, *args, **kwargs):
        self.request_user = kwargs.pop("request_user", None)
        super().__init__(*args, **kwargs)

        if self.request_user:
            self.fields["real_user"].queryset = User.objects.exclude(
                id=self.request_user.id
            )

        # tous optionnels par défaut
        for field in self.fields:
            self.fields[field].required = False

    def clean(self):
        cleaned = super().clean()
        ru = cleaned.get("real_user")
        ctype = cleaned.get("client_type")

        if ru:
            return cleaned

        if ctype == "user":
            required = ["first_name", "last_name", "email"]
        else:
            required = ["business_name"]

        missing = [f for f in required if not cleaned.get(f)]
        if missing:
            raise forms.ValidationError(
                "Veuillez remplir les champs obligatoires selon le type de client."
            )

        return cleaned

    def save(self, commit=True):
        client = super().save(commit=False)
        ru = self.cleaned_data.get("real_user")

        if ru:
            client.real_user = ru
            client.phone = getattr(ru, "phone", client.phone)
            client.address = getattr(ru, "address", client.address)

            if ru.user_type == "simple":
                try:
                    sp = ru.simple
                    client.client_type = "user"
                    client.first_name = sp.first_name
                    client.last_name = sp.last_name
                    client.email = ru.email
                except SimpleProfile.DoesNotExist:
                    client.is_anonymous = True

            elif ru.user_type == "business":
                try:
                    bp = ru.businessprofile
                    client.client_type = ru.role
                    client.business_name = bp.business_name
                except BusinessProfile.DoesNotExist:
                    client.is_anonymous = True

        if self.request_user and not client.pk:
            client.created_by = self.request_user

        if commit:
            client.save()
            self.save_m2m()

        return client


# =========================================================
# 6. EMPLOYÉ
# =========================================================
class EmployeeForm(forms.ModelForm):

    user = forms.ModelChoiceField(
        queryset=CustomUser.objects.none(),
        required=False,
        label="Itilizatè ekziste"
    )

    class Meta:
        model = Employee
        fields = [
            "business",
            "user",
            "first_name",
            "last_name",
            "email",
            "address",
            "phone",
            "employee_type",
            "position",
        ]

    def __init__(self, *args, **kwargs):
        self.business_user = kwargs.pop("business_user", None)
        super().__init__(*args, **kwargs)

        if self.business_user:
            biz = BusinessProfile.objects.filter(user=self.business_user).first()
            if biz:
                self.fields["business"].initial = biz
                self.fields["business"].widget = forms.HiddenInput()
                self.fields["business"].required = False

                self.fields["user"].queryset = CustomUser.objects.exclude(
                    employee__isnull=False
                )

    def clean(self):
        cleaned = super().clean()
        user = cleaned.get("user")

        if not user:
            required = ["first_name", "last_name", "email"]
            missing = [f for f in required if not cleaned.get(f)]
            if missing:
                raise forms.ValidationError(
                    "Veuillez renseigner les informations de l’employé."
                )

        return cleaned

    def save(self, commit=True):
        emp = super().save(commit=False)
        user = self.cleaned_data.get("user")

        if user:
            emp.user = user
            emp.first_name = user.first_name
            emp.last_name = user.last_name
            emp.email = user.email
            emp.phone = getattr(user, "phone", "")
            emp.address = getattr(user, "address", "")

        if commit:
            emp.save()

        return emp


# =========================================================
# 7. LOGIN
# =========================================================
class LoginAttemptForm(forms.Form):
    email = forms.EmailField(label="Adresse email")
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            raise forms.ValidationError("Veuillez entrer votre email.")
        return email


class LoginHistoryForm(forms.ModelForm):

    class Meta:
        model = LoginHistory
        fields = [
            "user", "ip_address", "user_agent",
            "device_type", "country", "city"
        ]
        widgets = {
            f: forms.TextInput(attrs={"readonly": "readonly"})
            for f in fields
        }