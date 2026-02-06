from rest_framework import serializers
from .models import (
    CustomUser,
    SimpleProfile,
    BusinessProfile,
    Client,
    Employee,
    LoginAttempt,
    LoginHistory,
)

# ============================================================
#  UTILISATEUR : SERIALIZER
# ============================================================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "phone",
            "user_type",
            "is_active",
        ]


# ============================================================
#  CREATION UTILISATEUR SIMPLE
# ============================================================
class RegisterSimpleUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["email", "phone", "password"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        simple_data = {
                   "first_name": validated_data.pop("first_name"),
                   "last_name": validated_data.pop("last_name"),
                   "address": validated_data.pop("address"),
            "driver_license_number": validated_data.pop("driver_license_number"),
            "driver_license_image": validated_data.pop("driver_license_image"),
        }
        user = CustomUser(**validated_data, user_type="simple")
        user.set_password(password)
        user.save()

        # Création automatique du profil simple
        SimpleProfile.objects.create(user=user, **simple_data)

        return user


# ============================================================
# 🔹 CREATION UTILISATEUR BUSINESS
# ============================================================
class RegisterBusinessUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    # champs business pour validation mais ne pas créer BusinessProfile ici
    business_name = serializers.CharField(write_only=True)
    address = serializers.CharField(write_only=True)
    patente_number = serializers.CharField(write_only=True)
    patente_image = serializers.ImageField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "phone",
            "password",
            "business_name",
            "address",
            "patente_number",
            "patente_image",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")

        # On peut stocker temporairement les données business pour validation
        validated_data['_business_data'] = {
            "business_name": validated_data.pop("business_name"),
            "address": validated_data.pop("address"),
            "patente_number": validated_data.pop("patente_number"),
            "patente_image": validated_data.pop("patente_image"),
        }

        user = CustomUser(**validated_data, user_type="business")
        user.set_password(password)
        user.save()  # le signal créera automatiquement BusinessProfile

        return user

# ============================================================
#  PROFILE UTILISATEUR SIMPLE
# ============================================================
class SimpleProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True, required=False)
    phone = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = SimpleProfile
        fields = [
            "email",
            "phone",
            "first_name",
            "last_name",
            "address",
            "driver_license_number",
            "driver_license_image",
        ]

    def update(self, instance, validated_data):
        user = instance.user

        # Mise à jour CustomUser si email/phone changent
        if "email" in validated_data:
            user.email = validated_data.pop("email")

        if "phone" in validated_data:
            user.phone = validated_data.pop("phone")

        user.save()

        return super().update(instance, validated_data)


# ============================================================
#  PROFILE BUSINESS
# ============================================================
class BusinessProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True, required=False)
    phone = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = BusinessProfile
        fields = [
            "email",
            "phone",
            "business_name",
            "address",
            "patente_number",
            "patente_image",
        ]

    def update(self, instance, validated_data):
        user = instance.user

        if "email" in validated_data:
            user.email = validated_data.pop("email")

        if "phone" in validated_data:
            user.phone = validated_data.pop("phone")

        user.save()

        return super().update(instance, validated_data)


# ============================================================
#  CLIENT
# ============================================================
class ClientSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Client
        fields = ["id", "user"]

# ============================================================
#  EMPLOYEE
# ============================================================
class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    business_name = serializers.CharField(source="business.business_name", read_only=True)

    class Meta:
        model = Employee
        fields = ["id", "name", "email", "phone", "position", "business", "business_name", "user"]
        
# ============================================================
#  LOGIN ATTEMPT
# ============================================================
class LoginAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginAttempt
        fields = [
            "id",
            "email",
            "ip_address",
            "status",
            "timestamp",
        ]


# ============================================================
#  LOGIN HISTORY
# ============================================================
class LoginHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginHistory
        fields = [
            "id",
            "user",
            "ip_address",
            "country",
            "city",
            "device",
            "timestamp",
        ]