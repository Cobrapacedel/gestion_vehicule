from django.urls import path
from rest_framework.routers import DefaultRouter
from . import api_views

app_name = "users_api"

urlpatterns = [
    # ==============================
    #  AUTHENTIFICATION
    # ==============================
    path("login/", api_views.APILoginView.as_view(), name="login"),       # JWT login
    path("logout/", api_views.APILogoutView.as_view(), name="logout"),    # JWT logout / blacklist

    # ==============================
    #  PROFIL UTILISATEUR SIMPLE
    # ==============================
    path("simple/", api_views.APISimpleProfileView.as_view(), name="simple_profile"),          # GET
    path("simple/update/", api_views.APISimpleProfileUpdateView.as_view(), name="simple_profile_update"),  # PUT/PATCH

    # ==============================
    #  PROFIL BUSINESS
    # ==============================
    path("business/", api_views.APIBusinessProfileView.as_view(), name="business_profile"),       # GET
    path("business/update/", api_views.APIBusinessProfileUpdateView.as_view(), name="business_profile_update"),  # PUT/PATCH

    # ==============================
    #  HISTORIQUE ET TENTATIVES DE LOGIN
    # ==============================
    path("login-history/", api_views.APILoginHistoryView.as_view(), name="login_history"),
    path("login-attempts/", api_views.APILoginAttemptView.as_view(), name="login_attempts"),
]

# ==============================
# ROUTER POUR UTILISATEURS ET CLIENTS
# ==============================
router = DefaultRouter()
router.register(r"users", api_views.APIUserViewSet, basename="user")       # list, retrieve, create, update, delete
router.register(r"clients", api_views.APIClientViewSet, basename="client") # list, retrieve, create, update, delete
router.register(r"employees", api_views.APIEmployeeViewSet, basename="employee")

urlpatterns += router.urls