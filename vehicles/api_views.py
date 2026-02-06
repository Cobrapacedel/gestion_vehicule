from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Vehicle, VehicleTransfer
from .serializers import VehicleSerializer, VehicleTransferSerializer

class VehicleListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Vehicle.objects.filter(owner=self.request.user).order_by("-id")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user, status='available')

class VehicleDetailAPIView(generics.RetrieveAPIView):
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Vehicle.objects.filter(owner=self.request.user)

class VehicleTransferAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = VehicleTransferSerializer(data=request.data)
        if serializer.is_valid():
            vehicle = serializer.validated_data['vehicle']
            new_owner = serializer.validated_data['new_owner']

            if vehicle.owner != request.user:
                return Response({'detail': 'Vous ne pouvez transférer que vos propres véhicules.'}, status=403)

            if new_owner == request.user:
                return Response({'detail': 'Impossible de vous transférer le véhicule.'}, status=400)

            vehicle.owner = new_owner
            vehicle.status = 'transferred'
            vehicle.save()
            serializer.save(previous_owner=request.user)

            return Response({'detail': 'Transfert effectué avec succès.'}, status=200)

        return Response(serializer.errors, status=400)