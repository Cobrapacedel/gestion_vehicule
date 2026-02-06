from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "users"

urlpatterns = [

    # ============================================================
    #  AUTHENTIFICATION
    # ============================================================
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # ============================================================
    #  INSCRIPTION
    # ============================================================
    path("register/", views.register_user, name="register_user"),                       # simple user
    path("register/business/", views.register_business, name="register_business"),     # business
    path("register-choice/", views.register_choice, name="register_choice"),

    # ============================================================
    #  PROFIL UTILISATEUR SIMPLE
    # ============================================================
    path("simple/", views.simple_profile_detail, name="simple_profile_detail"),
    path("simple/create/", views.simple_profile_create, name="simple_profile_create"),
    path("simple/update/", views.simple_profile_update, name="simple_profile_update"),
    path("simple/delete/", views.simple_profile_delete, name="simple_profile_delete"),

    # ============================================================
    #  PROFIL BUSINESS
    # ============================================================
    path("business/", views.business_profile_detail, name="business_profile_detail"),
    path("business/create/", views.business_profile_create, name="business_profile_create"),
    path("business/update/", views.business_profile_update, name="business_profile_update"),
    path("business/delete/", views.business_profile_delete, name="business_profile_delete"),

    # ============================================================
    #  MOT DE PASSE (Django built-in)
    # ============================================================
    path(
        "password/change/",
        auth_views.PasswordChangeView.as_view(template_name="users/password_change.html"),
        name="password_change",
    ),
    path(
        "password/change/done/",
        auth_views.PasswordChangeDoneView.as_view(template_name="users/password_change_done.html"),
        name="password_change_done",
    ),
    path(
        "password/reset/",
        auth_views.PasswordResetView.as_view(template_name="users/password_reset.html"),
        name="password_reset",
    ),
    path(
        "password/reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "password/reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(template_name="users/password_reset_confirm.html"),
        name="password_reset_confirm",
    ),
    path(
        "password/reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"),
        name="password_reset_complete",
    ),
    
    # ============================================================
    #  LIEN D'INVITATION 
    # ============================================================
    path("invite/<str:code>/", views.invitation_redirect, name="invite"),
    
    # ============================================================
    #  EMPLOYÉS
    # ============================================================
    path("employees/", views.employee_list, name="employee_list"),
    path("employees/<int:pk>/", views.employee_detail, name="employee_detail"),
    path("employees/create/", views.employee_create, name="employee_create"),
    path("employees/<int:pk>/edit/", views.employee_update, name="employee_update"),
    path("employees/<int:pk>/delete/", views.employee_delete, name="employee_delete"),
    
    # ============================================================
    # CLIENTS
    # ============================================================
    path("clients/", views.client_list, name="client_list"),
    path("clients/create/", views.client_create, name="client_create"),
    path("clients/<int:pk>/", views.client_detail, name="client_detail"),
    path("clients/<int:pk>/update/", views.client_update, name="client_update"),
    path("clients/<int:pk>/delete/", views.client_delete, name="client_delete"),
    
    
    path("notifications/email/toggle/", views.toggle_email_notifications, name="toggle_email_notifications"),
    path("notifications/sms/toggle/", views.toggle_sms_notifications, name="toggle_sms_notifications"),
]