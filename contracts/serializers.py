from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta

from django.contrib.auth import get_user_model
from users.models import Employee
from vehicles.models import Vehicle
from .models import Contract

from vehicles.serializers import VehicleSerializer
from users.serializers import UserSerializer

User = get_user_model()


# =====================================================
#   SERIALIZER DU CONTRAT
# =====================================================
class ContractSerializer(serializers.ModelSerializer):

    old_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    new_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)

    old_user_details = UserSerializer(source="old_user", read_only=True)
    new_user_details = UserSerializer(source="new_user", read_only=True)
    vehicle_details = VehicleSerializer(source="vehicle", read_only=True)

    class Meta:
        model = Contract
        fields = [
            "id",
            "contract_type",
            "contract_status",

            "old_user",
            "new_user",
            "vehicle",

            "start_date",
            "end_date",

            "price",
            "penalty_fee",

            "service_type",
            "warranty_period",

            "created_by",
            "created_at",
            "updated_at",

            # Read details
            "old_user_details",
            "new_user_details",
            "vehicle_details",
        ]

        read_only_fields = ("created_at", "updated_at", "created_by")

    # ------------------------------------------------------
    #  🔍 VALIDATIONS SPÉCIFIQUES PAR TYPE DE CONTRAT
    # ------------------------------------------------------
    def validate(self, data):
        contract_type = data.get("contract_type")
        old_user = data.get("old_user")
        new_user = data.get("new_user")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        price = data.get("price")
        service_type = data.get("service_type")
        warranty_period = data.get("warranty_period")

        # Cas où le new_user n'est pas encore assigné (update)
        if new_user:
            # 1️⃣ Vérification : Un employee doit avoir un profil Employee
            if new_user.user_type == "employee":
                emp = Employee.objects.filter(user=new_user).first()
                if emp is None:
                    raise serializers.ValidationError(
                        "L'utilisateur employé n'a pas de profil valide."
                    )

        # 2️⃣ PRET : simple → simple, max 30 jours
        if contract_type == "loan":
            if old_user.user_type != "simple" or new_user.user_type != "simple":
                raise serializers.ValidationError("Les prêts sont uniquement entre utilisateurs simples.")

            if start_date and end_date:
                if (end_date - start_date).days > 30:
                    raise serializers.ValidationError("Le prêt ne peut pas dépasser 30 jours.")

        # 3️⃣ LOCATION : business → simple/business
        if contract_type == "rent":
            if old_user.user_type != "business":
                raise serializers.ValidationError("Seules les entreprises peuvent louer un véhicule.")

            if not start_date or not end_date:
                raise serializers.ValidationError("Les dates sont obligatoires pour une location.")

            if end_date <= start_date:
                raise serializers.ValidationError("La date de fin doit être supérieure à la date de début.")

        # 4️⃣ SERVICE : service_type obligatoire
        if contract_type == "service":
            if not service_type:
                raise serializers.ValidationError("Le type de service est obligatoire.")

            # Exemple de prix automatiques
            service_prices = {
                "oil_change": 1500,
                "brake_repair": 4000,
                "diagnostic": 1000,
            }

            if service_type in service_prices and not price:
                data["price"] = service_prices[service_type]

        # 5️⃣ VENTE : garantie optionnelle mais valide
        if contract_type == "sell":
            if warranty_period is not None and warranty_period < 0:
                raise serializers.ValidationError("La garantie doit être positive.")

        return data

    # ------------------------------------------------------
    #  🔧 created_by automatiquement
    # ------------------------------------------------------
    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)