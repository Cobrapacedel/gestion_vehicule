from django.urls import path
from . import views

app_name = "vehicles"

urlpatterns = [

    # =====================
    # Véhicules
    # ====================
    path('', views.vehicles_list, name='vehicles_list'),
    path('add/', views.add_vehicle, name='add_vehicle'),
    path('<int:vehicle_id>/detail/', views.vehicle_detail, name='vehicle_detail'),
    path('<int:pk>/update/', views.VehicleUpdateView.as_view(), name='vehicle_update'),
    
    path("managed/", views.managed_vehicles_list, name="managed_vehicles_list"),

    # =============================
    # Recherche
    # =============================
    path('search/', views.search_results, name='search_results'),

    # =============================
    # API Marques / Modèles
    # =============================
    path("ajax/get-brands/", views.get_brands, name="get_brands"),
    path("ajax/get-models/", views.get_models, name="get_models"),

    # =============================
# VehicleStatusHistory
# =============================
    path('vehicle/<int:vehicle_id>/status_history/', views.vehicle_status_history_list, name='vehicle_status_history_list'),
    path('vehicle/<int:vehicle_id>/status_history/add/', views.vehicle_status_history_add, name='vehicle_status_history_add'),
    path('vehicle/status_history/<int:history_id>/detail/', views.vehicle_status_history_detail, name='vehicle_status_history_detail'),
    path('vehicle/status_history/<int:history_id>/delete/', views.vehicle_status_history_delete, name='vehicle_status_history_delete'),
    path("htmx/owner-vehicles/", views.htmx_owner_vehicles, name="htmx_owner_vehicles"),
]