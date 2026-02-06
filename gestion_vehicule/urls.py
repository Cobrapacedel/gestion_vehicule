from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
#import debug_toolbar
from django.conf.urls import handler404, handler500
from django.shortcuts import render
from core.views import home
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # ✅ cette ligne est indispensable !
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path("admin/", admin.site.urls),
    path("", home, name='home'),
    path("users/", include("users.urls", namespace='users')),
    path("api/users/", include("users.api_urls")),
    path("core/", include("core.urls", namespace='core')),
    path("payments/", include("payments.urls", namespace='payments')),  # HTML
    path("api/payments/", include("payments.api_urls")),  # API
    path("contracts/", include("contracts.urls", namespace='contracts')),  # HTML
    path("api/contracts/", include("contracts.api_urls")),  # API
    path("otp/", include("otp.urls")),
    path("fines/", include("fines.urls", namespace='fines')),
    path("documents/", include("documents.urls", namespace='documents')),
    path("vehicles/", include("vehicles.urls", namespace='vehicles')),
    path("notifications/", include("notifications.urls", namespace="notifications")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("tolls/", include("tolls.urls", namespace="tolls")),
    
    
    #path("__debug__/", include(debug_toolbar.urls)),
]

def custom_404(request, exception):
    return render(request, "404.html", status=404)

def custom_500(request):
    return render(request, "500.html", status=500)

handler404 = custom_404
handler500 = custom_500


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)