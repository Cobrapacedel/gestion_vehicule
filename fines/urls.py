from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


# Créer un routeur pour l'API
router = DefaultRouter()
router.register(r'fines', views.FineViewSet, basename='fine')
router.register(r'fine-pays', views.FinePayViewSet, basename='fine_pay')

app_name = "fines"

urlpatterns = [
    path('', views.fine_list, name='fine_list'),
    path('pay/<int:fine_id>/', views.pay_fine, name='pay_fine'),
    path('fine_detail/<int:fine_id>/', views.fine_detail, name='fine_detail'),
    path('fine_update/<int:fine_id>/', views.fine_update, name='fine_update'),
    path('fine_delete/<int:fine_id>/', views.fine_delete, name='fine_delete'),
    path('fine_create/', views.fine_create, name='fine_create'),
    path('fine/', views.fine_payment_view, name='fine_payment'),
    path('deleted/export/csv/', views.export_deleted_fines_csv, name='export_deleted_fines_csv'),
    path('api/', include(router.urls)),  # URL pour l'API REST
]