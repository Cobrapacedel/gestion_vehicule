from django.urls import path
from .api_views import DashboardAPIView

urlpatterns = [
    path('dashboard/', DashboardAPIView.as_view(), name='dashboard-api'),
]
