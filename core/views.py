from django.shortcuts import render, get_object_or_404, redirect
from .models import ProjectInfo
from django.contrib.auth.decorators import login_required
from payments.models import Balance
from users.models import CustomUser, Profile
from vehicles.models import Vehicle
from notifications.models import Notification
from fines.models import Fine
import logging
from django.db.models.functions import TruncMonth
from django.db.models import Sum
from payments.models import Transaction, Wallet
import calendar
import json
import requests

logger = logging.getLogger(__name__)

@login_required
def dashboard_view(request, user_id=None):
    logger.info(f"Utilisateur connecté : {request.user.email} | ID : {request.user.id}")

    user = get_object_or_404(CustomUser, id=user_id) if user_id else request.user

    if user != request.user and not request.user.is_staff:
        logger.warning(f"Accès refusé au dashboard de l'utilisateur {user.id} par {request.user.id}")
        return redirect("core:dashboard", user_id=request.user.id)

    balance = Balance.objects.select_related("user").filter(user=user).first()
    solde_total_htg = balance.total_balance() if balance else 0

    wallet, _ = Wallet.objects.get_or_create(user=request.user)

    nombre_vehicules = Vehicle.objects.filter(owner=user).count()

    notifications = (
        Notification.objects.filter(user=user, is_read=False).count()
        if hasattr(user, "notifications")
        else 0
    )
    transactions = (
        Transaction.objects
        .filter(user=request.user)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )
    fines = (
        Fine.objects.filter(user=user).count()
        )
    
    profile = request.user.profile

    labels = [calendar.month_abbr[t['month'].month] for t in transactions]
    data = [float(t['total']) for t in transactions]

    context = {
        "context_user": user,
        "user_id": user.id,
        "solde_objet": balance,
        "solde_total_htg": solde_total_htg,
        "nombre_vehicules": nombre_vehicules,
        "notifications": notifications,
        "fines":
            fines,
        "profile": profile,
        'labels': json.dumps(labels),
        'data': json.dumps(data),
    }

    return render(request, "core/dashboard.html", context)

def home(request):
    return render(request, "core/home.html")

def mon_cv_view(request):
    return render(request, "core/mon_cv.html")

def about_view(request):
    project = ProjectInfo.objects.first()
    if project:
        project = {
            "name": project.name,
            "version": project.version,
            "developer": project.developer,
            "contact_email": project.contact_email,
        }
    else:
        project = {}
    return render(request, "core/about.html", {"project": project})
    
def api_data_view(request):
    url = "https://api.exemple.com/data"  # Remplacez par l'URL réelle
    headers = {
        "Authorization": "Bearer VOTRE_CLÉ_API",  # Facultatif
        "Accept": "application/json",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        data = {"error": str(e)}

    return render(request, "external_api_page.html", {"data": data})

def handler404(request, exception):
    return render(request, '/404.html', status=404)

def handler500(request):
    return render(request, '/500.html', status=500)
