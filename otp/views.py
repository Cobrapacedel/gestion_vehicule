from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, authenticate, login
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import secrets

from .models import OTP
from .serializers import OTPSerializer
from .forms import OTPVerificationForm
from .utils import send_otp

User = get_user_model()

# === DRF ViewSet ===
class OTPViewSet(viewsets.ModelViewSet):
    queryset = OTP.objects.all()
    serializer_class = OTPSerializer

    @action(detail=False, methods=['post'])
    def generate(self, request):
        user_id = request.data.get('user_id')
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "Utilisateur non trouvé."}, status=status.HTTP_404_NOT_FOUND)

        OTP.objects.filter(user=user).delete()
        otp = OTP.create_otp(user=user, otp_type='login', delivery_method='email')
        try:
            send_otp(user, otp)
            return Response({"detail": f"OTP envoyé via {otp.delivery_method}."}, status=200)
        except Exception as e:
            return Response({"detail": f"Erreur d'envoi : {str(e)}"}, status=500)


# === Vues classiques ===
@login_required
def generate_otp(request):
    if request.method == "POST":
        OTP.objects.filter(user=request.user).delete()
        otp = OTP.create_otp(user=request.user, otp_type='login', delivery_method='email')
        send_otp(request.user, otp)
        return JsonResponse({"status": "success", "message": "OTP envoyé."})
    return render(request, 'otp/generate_otp.html')


@login_required
def resend_otp(request):
    if request.method == "POST":
        OTP.objects.filter(user=request.user).delete()
        otp = OTP.create_otp(user=request.user, otp_type='login', delivery_method='email')
        send_otp(request.user, otp)
        return JsonResponse({"status": "success", "message": "Nouveau code OTP envoyé."})
    return render(request, 'otp/resend_otp.html')


@login_required
def verify_otp(request):
    if request.method == "POST":
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            otp_entry = OTP.objects.filter(user=request.user, code=code, is_used=False).first()
            if otp_entry and otp_entry.is_valid():
                request.user.is_verified = True
                request.user.save()
                otp_entry.is_used = True
                otp_entry.save()
                messages.success(request, "Le code est valide.")
                return redirect("core:dashboard")
            else:
                messages.error(request, "Code incorrect ou expiré.")
        else:
            messages.error(request, "Formulaire invalide.")
    else:
        form = OTPVerificationForm()
    return render(request, "otp/verify_otp.html", {"form": form})


@login_required
def request_otp(request):
    user = request.user
    if request.method == "POST":
        otp_type = request.POST.get("otp_type", "login")
        delivery_method = request.POST.get("delivery_method", "email")

        if delivery_method == 'sms' and not user.phone_number:
            messages.error(request, "Vous n'avez pas de numéro de téléphone.")
            return redirect('profile')

        OTP.objects.filter(user=user).delete()
        otp = OTP.create_otp(user=user, otp_type=otp_type, delivery_method=delivery_method)

        try:
            send_otp(user, otp)
            messages.success(request, f"Code envoyé par {delivery_method}.")
        except Exception as e:
            messages.error(request, f"Erreur lors de l'envoi : {str(e)}")

        return redirect('otp:verify_otp')

    return render(request, "otp/request_otp.html", {
        'otp_types': OTP.OTP_TYPES,
        'delivery_methods': OTP.DELIVERY_METHODS,
    })