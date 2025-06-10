from django.urls import path
from .views import (
    UserRegistrationView,
    user_login,
    profile_detail,
    ProfileUpdateView,
    user_logout
)
from . import views

app_name = "users"

urlpatterns = [
    # User Registration
    path("register/", UserRegistrationView.as_view(), name="register"),

    # User Login
    path("login/", user_login, name="login"),

    # Profile Management
    path("profile/", profile_detail, name="profile"),
    path("profile/<int:user_id>/", profile_detail, name="profile"),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile-update"),
    
    path("toggle/email/", views.toggle_email_notifications, name="toggle_email_notifications"),
    path("toggle/sms/", views.toggle_sms_notifications, name="toggle_sms_notifications"),

    # Logout
    path("logout/", user_logout, name="logout"),
]