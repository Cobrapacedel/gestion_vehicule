import qrcode
import io
import base64
from django.utils.timezone import now
from rest_framework import serializers
from payments.models import Balance, Transaction, Payment
from .models import DocumentRenewal
from vehicles.models import Vehicle
from payments.serializers import PaymentSerializer

# ✅ Serializer for document renewal
class DocumentRenewalSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    vehicle = serializers.StringRelatedField()
    payment = PaymentSerializer(read_only=True)

    class Meta:
        model = DocumentRenewal
        fields = ["id", "user", "vehicle", "document_type", "amount", "currency", "expiration_date", "paid", "payment"]