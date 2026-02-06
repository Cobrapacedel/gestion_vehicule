from django.urls import path
from . import views

app_name = "core"

# Déclaration de la liste des URLs
urlpatterns = [
    path('', views.home, name='home'),
    path("dashboard/", views.dashboard_redirect, name="dashboard_redirect"),
    path("dashboard/user/", views.dashboard_user, name="dashboard_user"),
    path("dashboard/business/", views.dashboard_business, name="dashboard_business"),
   # path("dashboard/service/", views.dashboard_service, name="dashboard_service"),
    #path('dashboard/', views.dashboard_view, name='dashboard'),
    #path('dashboard/<int:user_id>/', views.dashboard_view, name='dashboard_with_user_id'),
    path('about/', views.about_view, name='about'),
    path('mon_cv/', views.cv_view, name='mon_cv'),

    # Redirection après login
    #path("redirect-after-login/", views.redirect_after_login, name="redirect_after_login"),

    # Gestion des erreurs
    # Ces handlers sont déclarés dans urls.py principal du projet
    # handler404 = "core.views.handler404"
    # handler500 = "core.views.handler500"
]
    

