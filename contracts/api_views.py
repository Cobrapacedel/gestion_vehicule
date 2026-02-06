from rest_framework import generics, permissions, status, viewsets, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Contract
from .serializers import ContractSerializer
from django.contrib.auth import get_user_model
from .utils import apply_rental_penalty

User = get_user_model()

# -----------------------------------------------------
# Permissions personnalisées
# -----------------------------------------------------
class IsEmployeeOrOwner(permissions.BasePermission):
    """Seuls les employés business, créateurs ou admins peuvent modifier un contrat."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if hasattr(request.user, "employee") and request.user.employee is not None:
            return True
        return obj.created_by == request.user


# -----------------------------------------------------
# Contract API
# -----------------------------------------------------
class ContractListCreateAPIView(generics.ListCreateAPIView):
    queryset = Contract.objects.select_related("old_user", "new_user", "vehicle")
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["vehicle__plate_number", "old_user__email", "new_user__email"]
    ordering_fields = ["created_at", "price"]

    def get_queryset(self):
        qs = super().get_queryset()
        contract_type = self.request.GET.get("contract_type")
        if contract_type:
            qs = qs.filter(contract_type=contract_type)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ContractRetrieveUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Contract.objects.select_related("old_user", "new_user", "vehicle")
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmployeeOrOwner]

    def perform_update(self, serializer):
        instance = serializer.save()

        # Applique pénalité automatique si location
        if instance.contract_type == Contract.CONTRACT_RENT:
            if instance.rent_end_date:
                today = timezone.now().date()
                if today > instance.rent_end_date:
                    instance.penalty_amount = (today - instance.rent_end_date).days * (instance.rent_price or 0)
                    instance.save()


# -----------------------------------------------------
# Appliquer pénalité manuellement via API
# -----------------------------------------------------
from rest_framework.views import APIView

class ApplyPenaltyAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        contract = get_object_or_404(Contract, pk=pk)

        if contract.contract_type != Contract.CONTRACT_RENT:
            raise ValidationError("Seuls les contrats de location ont des pénalités.")

        today = timezone.now().date()

        if not contract.rent_end_date or today <= contract.rent_end_date:
            return Response({"message": "Aucune pénalité à appliquer."})

        delay_days = (today - contract.rent_end_date).days
        penalty = delay_days * (contract.rent_price or 0)

        contract.penalty_amount = penalty
        contract.save()

        return Response({
            "message": "Pénalité appliquée.",
            "penalty_amount": penalty,
            "days_late": delay_days
        })


# -----------------------------------------------------
# ContractViewSet
# -----------------------------------------------------
class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.select_related("old_user", "new_user", "vehicle")
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=["get"])
    def payments(self, request, pk=None):
        contract = self.get_object()
        payments = ContractPayment.objects.filter(contract=contract)
        serializer = ContractPaymentSerializer(payments, many=True)
        return Response(serializer.data)