from rest_framework import serializers
from .models import Renter, Seller, TransferredTo, Mechanic, Vehicle, VehicleTransfer

class RenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Renter
        fields = '__all__'


class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = '__all__'


class TransferredToSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferredTo
        fields = '__all__'


class MechanicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mechanic
        fields = '__all__'


class VehicleSerializer(serializers.ModelSerializer):
    seller = SellerSerializer()
    renter = RenterSerializer()
    transferred_to = TransferredToSerializer()
    mechanic = MechanicSerializer()

    class Meta:
        model = Vehicle
        fields = '__all__'

    def create(self, validated_data):
        seller_data = validated_data.pop('seller')
        renter_data = validated_data.pop('renter', None)
        transferred_to_data = validated_data.pop('transferred_to', None)
        mechanic_data = validated_data.pop('mechanic', None)

        seller = Seller.objects.create(**seller_data)
        renter = Renter.objects.create(**renter_data) if renter_data else None
        transferred_to = TransferredTo.objects.create(**transferred_to_data) if transferred_to_data else None
        mechanic = Mechanic.objects.create(**mechanic_data) if mechanic_data else None

        vehicle = Vehicle.objects.create(
            seller=seller,
            renter=renter,
            transferred_to=transferred_to,
            mechanic=mechanic,
            **validated_data
        )
        return vehicle


class VehicleTransferSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer()
    previous_owner = serializers.StringRelatedField()
    new_owner = serializers.StringRelatedField()

    class Meta:
        model = VehicleTransfer
        fields = '__all__'
