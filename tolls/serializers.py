from rest_framework import serializers
from .models import Toll, TollTransaction, TollBooth
from vehicles.models import Vehicle  # Si tu as un modèle Vehicle dans une autre application


class TollBoothSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les stations de péage"""
    class Meta:
        model = TollBooth
        fields = ['id', 'name', 'location', 'price']


class VehicleSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les véhicules"""
    class Meta:
        model = Vehicle
        fields = ['id', 'plate_number', 'make', 'model', 'owner']  # Ajuste en fonction des champs de ton modèle


class TollSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les paiements de péage"""
    toll_booth = TollBoothSerializer()  # Détails du péage
    vehicle = VehicleSerializer()  # Détails du véhicule
    
    class Meta:
        model = Toll
        fields = ['id', 'user', 'vehicle', 'toll_booth', 'amount', 'payment_method', 'timestamp']
        read_only_fields = ['user', 'timestamp']
    
    def create(self, validated_data):
        """Crée un paiement de péage en associant l'utilisateur connecté"""
        toll_booth_data = validated_data.pop('toll_booth')
        vehicle_data = validated_data.pop('vehicle')
        
        toll_booth = TollBooth.objects.get(id=toll_booth_data['id'])
        vehicle = Vehicle.objects.get(id=vehicle_data['id'])
        
        toll = Toll.objects.create(
            toll_booth=toll_booth,
            vehicle=vehicle,
            user=self.context['request'].user,  # Associe l'utilisateur connecté
            **validated_data
        )
        return toll


class TollTransactionSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les transactions de péage"""
    toll = TollSerializer()  # Détails du péage
    vehicle = VehicleSerializer()  # Détails du véhicule
    
    class Meta:
        model = TollTransaction
        fields = ['id', 'user', 'vehicle', 'toll', 'amount_paid', 'date_passed']
        read_only_fields = ['user', 'date_passed']
    
    def create(self, validated_data):
        """Crée une transaction de paiement associée à un péage"""
        toll_data = validated_data.pop('toll')
        vehicle_data = validated_data.pop('vehicle')
        
        toll = Toll.objects.get(id=toll_data['id'])
        vehicle = Vehicle.objects.get(id=vehicle_data['id'])
        
        transaction = TollTransaction.objects.create(
            toll=toll,
            vehicle=vehicle,
            user=self.context['request'].user,  # Associe l'utilisateur connecté
            **validated_data
        )
        return transaction
