from django.shortcuts import render
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import DocumentRenewal
from .serializers import DocumentRenewalSerializer
from .permissions import IsOwnerOrAdmin  # ✅ Ajout de la permission

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

# Liste des renouvellements de documents
class DocumentRenewalListView(generics.ListAPIView):
    serializer_class = DocumentRenewalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:  # ✅ Un admin voit tout
            return DocumentRenewal.objects.all()
        return DocumentRenewal.objects.filter(user=self.request.user)  # ✅ Un utilisateur normal voit seulement ses documents


# VueSet pour gérer la création/modification/suppression
class DocumentRenewalViewSet(viewsets.ModelViewSet):
    queryset = DocumentRenewal.objects.all()
    serializer_class = DocumentRenewalSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]  # ✅ Restriction d'accès

    def get_queryset(self):
        if self.request.user.is_staff:  
            return DocumentRenewal.objects.all()
        return DocumentRenewal.objects.filter(user=self.request.user)

# Paiement d'un renouvellement de document
class PayDocumentRenewalView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, renewal_id):
        """Payer un renouvellement de document."""
        try:
            renewal = get_object_or_404(DocumentRenewal, id=renewal_id, user=request.user, paid=False)
        except DocumentRenewal.DoesNotExist:
            return Response({"error": "Renouvellement non trouvé ou déjà payé"}, status=status.HTTP_404_NOT_FOUND)

        balance = Balance.objects.get(user=request.user)
        if balance.debit(renewal.amount, renewal.currency):
            payment = Payment.objects.create(
                user=request.user, amount=renewal.amount, currency=renewal.currency, payment_type="renewal"
            )
            renewal.payment = payment
            renewal.paid = True
            renewal.save()
            return Response({"message": "Renouvellement payé avec succès"}, status=status.HTTP_200_OK)
        
        return Response({"error": "Fonds insuffisants"}, status=status.HTTP_400_BAD_REQUEST)
        
def document_payment_view(request):
    return render(request, 'documents/document_payment_form.html')