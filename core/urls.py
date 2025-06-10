from django.urls import path
from .views import home, dashboard_view, about_view, api_data_view, mon_cv_view

app_name = "core"

urlpatterns = [
    path('dashboard/', dashboard_view, name='dashboard'),  # Route sans user_id
    path('dashboard/<int:user_id>/', dashboard_view, name='dashboard_with_user_id'),  # Route avec user_id
    path('about/', about_view, name='about'),
    path('api-externe/', api_data_view, name='api_externe'),
    path("mon_cv/", mon_cv_view, name="mon_cv")
]