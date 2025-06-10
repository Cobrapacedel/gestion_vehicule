from django.urls import path
from . import views

app_name = "vehicles"

urlpatterns = [
    path("ajax/get-brands/", views.get_brands, name="get_brands"),
    path("ajax/get-models/", views.get_models, name="get_models"),
    path("add/", views.add_vehicle, name="add_vehicle"),
    path("list/", views.vehicles_list, name="vehicles_list"),
    path("<int:vehicle_id>/", views.vehicle_status, name="vehicle_status"),
    path("search/", views.search_results, name="search_results"),
    path("transfer/", views.transfer_vehicle, name="transfer_vehicle"),
]