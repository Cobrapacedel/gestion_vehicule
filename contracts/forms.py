from decimal import Decimal
from django import forms
from django.utils import timezone

from users.models import CustomUser, Employee
from vehicles.models import Vehicle
from contracts.models import Contract, ServiceType


# ======================================================
#                    CONTRACT FORM
# ======================================================

class ContractForm(forms.ModelForm):

    class Meta:
        model = Contract
        fields = [
            "contract_type",
            "new_user",
            "vehicle",
            "start_date",
            "end_date",
            "price",
            "is_paid",
            "penalty_per_day",
            "warranty_period",
            "service_type",
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.created_by = kwargs.pop("created_by", None)
        super().__init__(*args, **kwargs)

        # --------------------------------------------------
        # old_user = utilisateur connecté
        # --------------------------------------------------
        if self.user:
            self.instance.old_user = self.user

        # --------------------------------------------------
        # new_user = tous sauf utilisateur connecté
        # --------------------------------------------------
        if self.user:
            self.fields["new_user"].queryset = CustomUser.objects.exclude(
                id=self.user.id
            )

        # --------------------------------------------------
        # vehicle = véhicules appartenant au user
        # --------------------------------------------------
        if self.user:
            self.fields["vehicle"].queryset = Vehicle.objects.filter(
                owner=self.user
            )
        else:
            self.fields["vehicle"].queryset = Vehicle.objects.none()

        # --------------------------------------------------
        # service_type = services actifs
        # --------------------------------------------------
        self.fields["service_type"].queryset = ServiceType.objects.filter(
            is_active=True
        )

        # --------------------------------------------------
        # Tous ces champs sont optionnels par défaut
        # (la vraie validation est dans clean())
        # --------------------------------------------------
        for field in [
            "vehicle",
            "start_date",
            "end_date",
            "price",
            "penalty_per_day",
            "warranty_period",
            "service_type",
        ]:
            self.fields[field].required = False

    # ======================================================
    #                      VALIDATION
    # ======================================================
    def clean(self):
        cleaned = super().clean()

        contract_type = cleaned.get("contract_type")
        new_user = cleaned.get("new_user")
        old_user = self.instance.old_user
        role = getattr(self.user, "role", None)

        # --------------------------------------------------
        # Nettoyage par type
        # --------------------------------------------------
        if contract_type != Contract.CONTRACT_SERVICE:
            cleaned["service_type"] = None

        if contract_type in [Contract.CONTRACT_LOAN, "transfer"]:
            cleaned["price"] = None

        # --------------------------------------------------
        # RÈGLES PAR RÔLE
        # --------------------------------------------------
        allowed_contracts = {
            "agency": ["rent", "service"],
            "dealer": ["sell", "transfer", "service"],
            "garage": ["service", "sell"],
            "user": ["loan", "sell", "rent", "service", "transfer"],
        }

        if role in allowed_contracts:
            if contract_type not in allowed_contracts[role]:
                raise forms.ValidationError(
                    "Vous n’êtes pas autorisé à créer ce type de contrat."
                )

        # --------------------------------------------------
        # EMPLOYÉ → agit pour son entreprise
        # --------------------------------------------------
        if self.created_by and hasattr(self.created_by, "employee"):
            employee = Employee.objects.get(user=self.created_by)
            if old_user != employee.businessprofile.user:
                raise forms.ValidationError(
                    "L’employé doit créer le contrat pour son entreprise."
                )

        # --------------------------------------------------
        # PRÊT
        # --------------------------------------------------
        if contract_type == Contract.CONTRACT_LOAN:
            if (
                old_user.user_type != "simple"
                or new_user.user_type != "simple"
            ):
                raise forms.ValidationError(
                    "Un prêt est autorisé uniquement entre utilisateurs simples."
                )

            start = cleaned.get("start_date")
            end = cleaned.get("end_date")

            if not start or not end:
                raise forms.ValidationError(
                    "Les dates sont obligatoires pour un prêt."
                )

            if end <= start:
                raise forms.ValidationError(
                    "La date de fin doit être après la date de début."
                )

            if (end - start).days > 30:
                raise forms.ValidationError(
                    "Un prêt ne peut excéder 30 jours."
                )

        # --------------------------------------------------
        # LOCATION
        # --------------------------------------------------
        if contract_type == Contract.CONTRACT_RENT:
            if not cleaned.get("vehicle"):
                raise forms.ValidationError("Un véhicule est obligatoire.")

            if not cleaned.get("start_date") or not cleaned.get("end_date"):
                raise forms.ValidationError(
                    "Les dates sont obligatoires pour la location."
                )

            if not cleaned.get("penalty_per_day"):
                raise forms.ValidationError(
                    "La pénalité journalière est requise."
                )

            if not cleaned.get("price"):
                raise forms.ValidationError(
                    "Le prix de location est obligatoire."
                )

        # --------------------------------------------------
        # VENTE
        # --------------------------------------------------
        if contract_type == Contract.CONTRACT_SELL:
            if not cleaned.get("price"):
                raise forms.ValidationError("Le prix est obligatoire.")

            if not cleaned.get("warranty_period"):
                raise forms.ValidationError(
                    "La période de garantie est obligatoire."
                )

        # --------------------------------------------------
        # SERVICE
        # --------------------------------------------------
        if contract_type == Contract.CONTRACT_SERVICE:
            service = cleaned.get("service_type")

            if not service:
                raise forms.ValidationError(
                    "Le type de service est requis."
                )

            # 🔒 Prix imposé automatiquement
            cleaned["price"] = service.default_price

        # --------------------------------------------------
        # TRANSFERT
        # --------------------------------------------------
        if contract_type == "transfer":
            if not cleaned.get("vehicle"):
                raise forms.ValidationError("Un véhicule est obligatoire.")

        return cleaned