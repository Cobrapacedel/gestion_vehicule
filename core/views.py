from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils.translation import gettext as _
from decimal import Decimal
from users.decorators import verified_required
from payments.models import Balance
from vehicles.models import Vehicle
from contracts.models import Contract
from notifications.models import Notification
from fines.models import Fine
from payments.services.wallet_service import create_wallet_for_user
from users.models import Client, Employee, BusinessProfile, SimpleProfile 
from documents.models import Document
from django.contrib.auth import get_user_model
from core.utils import get_user_balances

User = get_user_model()

# =========================
#  Redirection automatique selon le rôle de l’utilisateur
# =========================
@login_required
@verified_required
def dashboard_redirect(request):
    user = request.user
    if user.role in ["dealer", "agency", "garage"]:
        return redirect("core:dashboard_business")
    else:
        return redirect("core:dashboard_user")


# ========================
#  DASHBOARD UTILISATEUR SIMPLE
# =========================
@login_required
def dashboard_user(request):
    # Récupère le profil simple lié à l'utilisateur
    user = request.user
    simple = getattr(user, "simple", None)
    
    DEFAULT_NETWORK = "btc"

    wallet = create_wallet_for_user(user=user, network=DEFAULT_NETWORK)
    
    # Debug info
    print("USER_TYPE =", request.user.user_type)
    print("EMAIL =", request.user.email)
    print("USER_ID =", request.user.id)
    print("ROLE =", request.user.role)
    print("WALLET BTC =", wallet)
    print("Wallet public_key =", wallet.public_key)

    balances = get_user_balances(user)

    vehicles = Vehicle.objects.filter(owner_simple=user)
    notifications = Notification.objects.filter(user=user, is_read=False)
    fines = Fine.objects.filter(driver=user, is_paid=False)
    documents = Document.objects.filter(user=user)
    clients = Client.objects.visible_for(request.user)
    contracts = Contract.objects.visible_for(user)

    stats_cards = [
        {"icon": "🚗", "title": "Veyikil", "count": vehicles.count(), "url": reverse("vehicles:vehicles_list")},
        {"icon": "🔔", "title": "Notifikasyon", "count": notifications.count(), "url": reverse("notifications:notification_list")},
        {"icon": "📄", "title": "Kontravansyon", "count": fines.count(), "url": reverse("fines:fine_list")},
        {"icon": "📁", "title": "Dokiman", "count": documents.count(), "url": reverse("documents:document_list")},
        {"icon": "💰", "title": "Kontra", "count": contracts.count(), "url": reverse("contracts:contract_list")},
        {"icon": "💰", "title": "Kliyan", "count": clients.count(), "url": reverse("users:client_list")},
    ]

    context = {
        "stats_cards": stats_cards,
        "wallet": wallet,
        "simple": simple,
        **balances,
        "vehicles": vehicles,
        "notifications": notifications,
        "fines": fines,
        "documents": documents,
        "contracts": contracts,
        "clients": clients,
    }

    return render(request, "core/dashboard_user.html", context)

# =========================
# DASHBOARD BUSINESS (Dealer, Location, Garage)
# =========================
@login_required
@verified_required
def dashboard_business(request):

    user = request.user
    businessprofile = getattr(user, "businessprofile", None)
    
    balances = get_user_balances(user)

    DEFAULT_NETWORK = "btc"

    wallet = create_wallet_for_user(user=user, network=DEFAULT_NETWORK)

    print("USER_TYPE =", user.user_type)
    print("EMAIL =", user.email)
    print("USER_ID =", user.id)
    print("ROLE =", user.role)
    print("WALLET BTC =", wallet)
    print("Wallet public_key =", wallet.public_key)

    role_display = {
        "dealer": "Konsesyonè",
        "agency": "Ajans Lokasyon",
        "garage": "Garaj",
    }.get(user.role, "Antrepriz")

    vehicles = Vehicle.objects.filter(owner=user)
    documents = Document.objects.filter(user=user)
    notifications = Notification.objects.filter(user=user, is_read=False)

    # 🔥 QuerySet centralisé
    contracts = Contract.objects.visible_for(user)

    clients = Client.objects.visible_for(user)
    employees = Employee.objects.filter(business__user=user)

    # Stats dynamiques selon rôle
    stats_cards = [
        {"icon": "🚗", "title": "Veyikil", "count": vehicles.count(), "url": reverse("vehicles:vehicles_list")},
        {"icon": "📁", "title": "Dokiman", "count": documents.count(), "url": reverse("documents:document_list")},
        {"icon": "🔔", "title": "Notifikasyon", "count": notifications.count(), "url": reverse("notifications:notification_list")},
        {"icon": "👥", "title": "Kliyan", "count": clients.count(), "url": reverse("users:client_list")},
    ]

    if user.role == "dealer":
        stats_cards += [
            {"icon": "💰", "title": "Kontra Vant", "count": contracts.sells().count(), "url": reverse("contracts:contract_list")},
            {"icon": "🛠︄", "title": "Kontra Sèvis", "count": contracts.services().count(), "url": reverse("contracts:contract_list")},
            {"icon": "👤", "title": "Anplwaye", "count": employees.count(), "url": reverse("users:employee_list")},
        ]

    elif user.role == "agency":
        stats_cards += [
            {"icon": "💼", "title": "Kontra Lokasyon", "count": contracts.rents().count(), "url": reverse("contracts:contract_list")},
            {"icon": "🛠", "title": "Kontra Sèvis", "count": contracts.services().count(), "url": reverse("contracts:contract_list")},
            {"icon": "👤", "title": "Anplwaye", "count": employees.count(), "url": reverse("users:employee_list")},
        ]

    elif user.role == "garage":
        stats_cards += [
            {"icon": "🛠︄", "title": "Kontra Sèvis", "count": contracts.services().count(), "url": reverse("contracts:contract_list")},
        ]

    context = {
        "businessprofile": businessprofile,
        "role_display": role_display,
        "wallet": wallet,
        "stats_cards": stats_cards,
        **balances,
        "vehicles": vehicles,
        "contracts": contracts,
        "documents": documents,
        "notifications": notifications,
        "clients": clients,
    }

    return render(request, "core/dashboard_business.html", context)

# ========================
#  PAGES GÉNÉRIQUES
# =========================
@login_required
def home(request):
    return render(request, "core/home.html")


@login_required
def about_view(request):
    project_info = {}
    try:
        from .models import ProjectInfo
        project = ProjectInfo.objects.first()
        if project:
            project_info = {
                "name": project.name,
                "version": project.version,
                "developer": project.developer,
                "contact_email": project.contact_email,
            }
    except ImportError:
        pass
    return render(request, "core/about.html", {"project": project_info})


@login_required
def cv_view(request):
    return render(request, "core/cv.html")


# =========================
#  HANDLERS D’ERREURS
# ========================
def handler404(request, exception):
    return render(request, "404.html", status=404)


def handler500(request):
    return render(request, "500.html", status=500)