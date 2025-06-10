from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentRenewalListView, PayDocumentRenewalView
from . import views
    
app_name = "documents" 

urlpatterns = [
   # Vue pour lister les renouvellements de documents
    path('document-renewals/', DocumentRenewalListView.as_view(), name="document_renewal_list"),

    # Vue pour payer un renouvellement de document
    path('document-renewals/<int:renewal_id>/pay/', PayDocumentRenewalView.as_view(), name="pay_document_renewal"),
    path('document/', views.document_payment_view, name='document_payment'),
]