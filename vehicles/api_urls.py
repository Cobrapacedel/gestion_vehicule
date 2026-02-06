from django.urls import path
from . import api_views

app_name = "vehicles_api"

urlpatterns = [
    path("list/", api_views.VehicleListCreateAPIView.as_view(), name="vehicle_list_create"),
    path("detail/<int:pk>/", api_views.VehicleDetailAPIView.as_view(), name="vehicle_detail"),
    path("transfer/", api_views.VehicleTransferAPIView.as_view(), name="vehicle_transfer"),
]