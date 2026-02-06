from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.contrib import messages
from .models import LoginAttempt, LoginHistory
from .utils import get_geolocation
from django.conf import settings
from django.urls import reverse

class AccountLockMiddleware(MiddlewareMixin):
    """
    Middleware to handle account locking based on failed login attempts.
    Prevents access to the site if the user's account is temporarily locked.
    """
    def process_request(self, request):
        # Check if the user is authenticated and has a locked account
        if request.user.is_authenticated:
            try:
                login_attempt = LoginAttempt.objects.get(user=request.user)
                if login_attempt.is_locked():
                    messages.error(request, "Votre compte est temporairement verrouillé. Veuillez réessayer plus tard.")
                    return redirect("login")
            except LoginAttempt.DoesNotExist:
                pass  # No login attempts recorded for this user


class GeolocationLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log geolocation data for successful login attempts.
    """
    def process_response(self, request, response):
        # Log geolocation only for authenticated users and specific views (e.g., login)
        if request.user.is_authenticated and request.path == "/login/":
            ip_address = request.META.get("REMOTE_ADDR")
            user_agent = request.META.get("HTTP_USER_AGENT", "")
            city, country = get_geolocation(ip_address)

            # Save geolocation data to LoginHistory
            LoginHistory.objects.create(
                user=request.user,
                ip_address=ip_address,
                user_agent=user_agent,
                city=city,
                country=country,
            )
        return response


class SecurityMiddleware(MiddlewareMixin):
    """
    Middleware to enforce security measures such as HTTPS redirection and setting secure headers.
    """
    def process_request(self, request):
        # Redirect HTTP requests to HTTPS (optional, for production environments)
        if not request.is_secure() and not settings.DEBUG:
            url = request.build_absolute_uri(request.get_full_path()).replace("http://", "https://")
            return redirect(url)

    def process_response(self, request, response):
        # Set security-related headers
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["X-XSS-Protection"] = "1; mode=block"
        return response