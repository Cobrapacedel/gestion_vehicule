from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Recharge, Transaction, Payment, Balance
from .serializers import RechargeSerializer, TransactionSerializer, PaymentSerializer, BalanceSerializer

class RechargeViewSet(viewsets.ModelViewSet):
    serializer_class = RechargeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Recharge.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        recharge = self.get_object()
        if recharge.user != request.user:
            return Response({"detail": "Non autorisé."}, status=status.HTTP_403_FORBIDDEN)
        recharge.complete_recharge()
        return Response({"status": "Recharge complétée"})


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)


class BalanceViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        balance, _ = Balance.objects.get_or_create(user=request.user)
        serializer = BalanceSerializer(balance)
        return Response(serializer.data)