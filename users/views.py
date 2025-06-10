from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from otp.utils import generate_and_send_otp
from django.views.generic import CreateView, UpdateView, ListView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import CustomUser, Profile, LoginAttempt, LoginHistory
from .forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    ProfileUpdateForm,
)
from django.utils import timezone
from datetime import timedelta
from otp.models import OTP
from otp.forms import OTPVerificationForm
import requests
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import secrets
from django.conf import settings
import requests
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.http import HttpResponseRedirect

CustomUser = get_user_model()




# User Registration View
@method_decorator(csrf_protect, name='dispatch')
class UserRegistrationView(CreateView):
    """View for user registration."""
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        """Handle valid form submission with reCAPTCHA if enabled."""

        if settings.USE_RECAPTCHA:
            recaptcha_response = self.request.POST.get('g-recaptcha-response')
            if not recaptcha_response:
                messages.error(self.request, "Tanpri konfime ke ou pa yon robo.")
                return self.form_invalid(form)

            data = {
                'secret': settings.RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
            result = r.json()

            if not result.get('success'):
                messages.error(self.request, "Verifikasyon reCAPTCHA echwe.")
                return self.form_invalid(form)

        response = super().form_valid(form)
        user = self.object
        generate_and_send_otp(user)

        # Redirection vers la page de vérification OTP
        return redirect("otp:verify_otp")  # ou avec paramètres si besoin
        messages.success(self.request, "Kont kreye avèk siksè. Tanpri konekte.")
        return response

@csrf_protect
def user_login(request):
    form = CustomAuthenticationForm(request, data=request.POST or None)
    recaptcha_error = False

    if request.method == 'POST':
        if not settings.DEBUG:
            recaptcha_response = request.POST.get('g-recaptcha-response')
            if recaptcha_response:
                data = {
                    'secret': settings.RECAPTCHA_SECRET_KEY,
                    'response': recaptcha_response
                }
                r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
                result = r.json()
                if not result.get('success'):
                    recaptcha_error = True
            else:
                recaptcha_error = True

        if recaptcha_error:
            messages.error(request, "Tanpri konfime ke ou pa yon robo.")
            return render(request, "users/login.html", {"form": form, "recaptcha_error": True})

        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")

            user = get_user_model().objects.filter(email=email).first()
            if not user or not user.is_active:
                messages.error(request, "Kont lan pa valab oswa li dezaktive.")
                return redirect("login")

            login_attempt, _ = LoginAttempt.objects.get_or_create(user=user)
            if login_attempt.is_locked():
                messages.error(request, "Kont ou bloke tanporèman poutèt twòp tantativ rate.")
                return redirect("login")

            user = authenticate(request, email=email, password=password)
            if user:
                login_attempt.reset_attempts()

                # Si l'utilisateur n'est pas vérifié, on génère et envoie un OTP
                if not user.is_verified:
                    from otp.utils import generate_and_send_otp
                    generate_and_send_otp(user)

                    request.session["otp_user_id"] = user.id
                    return redirect("otp:verify_otp")

                # Connexion directe si vérifié
                login(request, user)

                ip_address = request.META.get("REMOTE_ADDR")
                user_agent = request.META.get("HTTP_USER_AGENT", "")
                LoginHistory.log_login(user=user, ip_address=ip_address, user_agent=user_agent)

                messages.success(request, "Koneksyon reyisi!")
                return redirect("core:dashboard")
            else:
                login_attempt.register_failed_attempt()
                messages.error(request, "Imèl oswa modpas pa kòrèk.")
        else:
            messages.error(request, "Tanpri korije erè yo.")

    return render(request, "users/login.html", {
        "form": form,
        "recaptcha_error": recaptcha_error
    })

# Profile Update View
@method_decorator(login_required, name="dispatch")
class ProfileUpdateView(UpdateView):
    """View for updating user profile."""
    model = Profile
    form_class = ProfileUpdateForm
    template_name = "users/update_profile.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        """Get the profile of the logged-in user."""
        return self.request.user.profile

    def form_valid(self, form):
        """Handle valid form submission."""
        messages.success(self.request, "Profil mis à jour avec succès.")
        return super().form_valid(form)

# Profile Detail View
@login_required
def profile_detail(request):
    """View for displaying user profile details."""
    profile = request.user.profile
    return render(request, "users/profile_detail.html", {"profile": profile})

@login_required
def update_profile(request):
    """
    View for updating the user's profile.
    """
    profile = request.user.profile

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Skip file uploads in Termux
            if "profile_picture" in request.FILES:
                messages.warning(request, "Les téléchargements de fichiers ne sont pas supportés dans cet environnement.")
            else:
                form.save()
                messages.success(request, "Votre profil a été mis à jour avec succès.")
                return redirect("users:profile_detail")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, "users/update_profile.html", {"form": form})
    
# Logout View
def user_logout(request):
    """View for logging out."""
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect("login")

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Profile

@require_POST
@login_required
def toggle_email_notifications(request):
    profile = request.user.profile
    profile.email_notifications = not profile.email_notifications
    profile.save()
    return JsonResponse({"status": "ok", "email_notifications": profile.email_notifications})

@require_POST
@login_required
def toggle_sms_notifications(request):
    profile = request.user.profile
    profile.sms_notifications = not profile.sms_notifications
    profile.save()
    return JsonResponse({"status": "ok", "sms_notifications": profile.sms_notifications})

