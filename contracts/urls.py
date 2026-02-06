from django.urls import path
from . import views

app_name = "contracts"

urlpatterns = [
    # --- CONTRACTS ---
    path("", views.contract_list, name="contract_list"),
    path("<int:pk>/", views.contract_detail, name="contract_detail"),
    path("create/", views.contract_create, name="contract_create"),
    path("<int:pk>/update/", views.contract_update, name="contract_update"),
    path("<int:pk>/delete/", views.contract_delete, name="contract_delete"),
    path("<int:pk>/pay/", views.contract_pay, name="contract_pay"),
]