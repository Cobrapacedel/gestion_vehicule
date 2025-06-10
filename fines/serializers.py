from rest_framework import serializers
from .models import Fine, FinePay, Violation

class FineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fine
        fields = ['id', 'user', 'license_driver', 'vehicle', 'violation', 'violation_date', 'paid', 'amount', 'currency']

class FinePaySerializer(serializers.ModelSerializer):
    class Meta:
        model = FinePay
        fields = ['id', 'fine', 'amount', 'currency', 'payment_date', 'transaction']

class ViolationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Violation
        fields = ['id', 'reason', 'amount', 'currency', 'description']