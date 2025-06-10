from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OTPViewSet, verify_otp, generate_otp, resend_otp, request_otp

router = DefaultRouter()
router.register(r'otps', OTPViewSet, basename='otp')

app_name = "otp"

urlpatterns = [
    path('', include(router.urls)),
        # OTP Verification
    path("verify_otp/", verify_otp, name="verify_otp"),

    # Resend OTP
    path("resend-otp/", resend_otp, name="resend-otp"),

    # Generate OTP (API endpoint)
    path("generate-otp/", generate_otp, name="generate-otp"),
    
    path("request-otp/", request_otp, name="request_otp"),
]