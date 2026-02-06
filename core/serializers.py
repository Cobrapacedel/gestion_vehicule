from rest_framework import serializers

class DashboardSerializer(serializers.Serializer):
    balance = serializers.DecimalField(max_digits=10, decimal_places=2)
    vehicles_count = serializers.IntegerField()
    notifications_count = serializers.IntegerField()
    unpaid_fines_count = serializers.IntegerField()
