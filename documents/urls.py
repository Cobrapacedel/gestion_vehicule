from django.urls import path
from . import views

app_name = "documents"

urlpatterns = [
# ==========================
# Document 
# ==========================
    path("document/", views.document_list, name="document_list"),
    path("document/create", views.document_create, name="document_form"),
    path("document/<int:pk>/detail/", views.document_detail, name="document_detail"),
    path("document/<int:pk>/update/", views.document_update, name="document_update"),
    path("document/<int:pk>/delete/", views.document_delete, name="document_delete"),
    
# ==========================
# Document Renewal 
# ==========================
    path("renewal/<int:pk>/create/", views.renewal_create, name="renewal_form"),
    path("pay/<int:pk>/create/", views.document_pay, name="document_payment_form"),
]