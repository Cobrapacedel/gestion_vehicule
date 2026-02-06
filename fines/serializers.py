from rest_framework import serializers
from .models import Fine, Violation

class FineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fine
        fields = ['id', 'user', 'license_driver', 'vehicle', 'violation', 'violation_date', 'paid', 'amount', 'currency']

class ViolationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Violation
        fields = ['id', 'reason', 'amount', 'currency', 'description']