from django.utils import timezone
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy, reverse
from datetime import timedelta
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q, Prefetch
from django.utils import timezone
from django.views.generic.edit import UpdateView
from django.conf import settings
from django.contrib.auth import get_user_model

# Importe les modèles nécessaires
from .models import Vehicle, VehicleStatusHistory
from .forms import VehicleForm, VehicleStatusHistoryForm
from .utils import VEHICLE_DATA

from contracts.models import Contract  # correction : import Contract
# autres modèles utilisés par contexte (fines, services, etc.) peuvent être importés si besoin

CustomUser = get_user_model()


# =============================
#  API Marques / Modèles
# =============================
@login_required
def get_brands(request):
    vehicle_type = request.GET.get("vehicle_type")
    brands = list(VEHICLE_DATA.get(vehicle_type, {}).keys())
    return JsonResponse({"brands": brands})


@login_required
def get_models(request):
    vehicle_type = request.GET.get("vehicle_type")
    brand = request.GET.get("brand")
    models = VEHICLE_DATA.get(vehicle_type, {}).get(brand, [])
    return JsonResponse({"models": models})


# =============================
# Ajout véhicule
# =============================
@login_required
def add_vehicle(request):
    if request.method == "POST":
        form = VehicleForm(request.POST, request.FILES)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.owner = request.user
            vehicle.save()

            # Réponse Ajax
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({
                    "success": True,
                    "message": "Veyikil anrejistre ak siksè !",
                    "redirect_url": reverse("vehicles:vehicles_list")
                })

            messages.success(request, "🚗 Yon nouvo veyikil ajoute sou kont ou!")
            return redirect("vehicles:vehicles_list")
        else:
            print("FORM ERRORS 👉", form.errors.as_json())
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({
                    "success": False,
                    "message": "Erè.",
                    "errors": form.errors
                })
            messages.error(request, "Korije erè yo.")
    else:
        form = VehicleForm()
    return render(request, "vehicles/add_vehicle.html", {"form": form})

# =============================
# Liste véhicules (propres à l'utilisateur)
# =============================
@login_required
def vehicles_list(request):
    user = request.user
    vehicles_qs = (
        Vehicle.objects.filter(owner=request.user)
        .select_related("owner", "dealer", "agency", "garage")
        .prefetch_related("fines")
        .order_by("-id")
    )
    paginator = Paginator(vehicles_qs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "vehicles/vehicles_list.html", {"vehicles": page_obj})


# =============================
# Liste véhicules gérés (par rôle) — HTMX friendly
# =============================
@login_required
def managed_vehicles_list(request):
    """Affiche la liste des véhicules gérés par l'utilisateur, avec recherche et pagination (HTMX)."""
    user = request.user
    query = request.GET.get("q", "").strip()

    # Détermine les véhicules que l'utilisateur peut gérer selon son rôle
    if getattr(user, "role", None) == "dealer":
        vehicles = Vehicle.objects.filter(owner_type=user)
    elif getattr(user, "role", None) == "agency":
        # Si tu as un champ agency sur Vehicle
        vehicles = Vehicle.objects.filter(agency=user) if hasattr(Vehicle, "agency") else Vehicle.objects.filter(owner_type=user)
    elif getattr(user, "role", None) == "garage":
        vehicles = Vehicle.objects.filter(owner=user)
    else:
        vehicles = Vehicle.objects.filter(owner=user)

    # Filtrage (recherche)
    if query:
        vehicles = vehicles.filter(
            Q(brand__icontains=query)
            | Q(model__icontains=query)
            | Q(plate_number__icontains=query)
            | Q(vehicle_type__icontains=query)
        )

    # Pagination (10 véhicules par page)
    paginator = Paginator(vehicles.order_by("-id"), 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "query": query,
    }

    # Si c’est une requête HTMX, on renvoie seulement la table partielle
    if request.headers.get("HX-Request"):
        return render(request, "vehicles/partials/vehicles_table.html", context)

    # Sinon, on renvoie la page complète
    return render(request, "vehicles/managed_vehicles_list.html", context)


# =============================
# Détail véhicule
# =============================
@login_required
def vehicle_detail(request, vehicle_id):
    vehicle = get_object_or_404(
        Vehicle.objects.select_related("owner").prefetch_related(
            "fines__violation",
            "status_history",
        ),
        id=vehicle_id
    )

    # 🔐 Sécurité : propriétaire ou rôle autorisé
    if vehicle.owner != request.user and request.user.role not in ["dealer", "agency", "garage"]:
        messages.error(request, _("Ou pa gen otorizasyon."))
        return redirect("vehicles:vehicles_list")

    # 🔑 Déterminer le propriétaire à afficher
    owner = vehicle.owner

    # 🚨 Amendes
    fines_qs = vehicle.fines.all().order_by("-issued_at")
    unpaid_fines = fines_qs.filter(is_paid=False)
    paid_fines = fines_qs.filter(is_paid=True)

    # 📊 Historique des statuts
    status_history = vehicle.status_history.all().order_by("-changed_at")

    # 📜 Tous les contrats liés au véhicule
    contracts = Contract.objects.filter(vehicle=vehicle).select_related(
        "old_user", "new_user", "service_type"
    ).order_by("-created_at")

    # 🎯 Séparation par type
    rentals   = contracts.filter(contract_type="rent")
    services  = contracts.filter(contract_type="service")
    sales     = contracts.filter(contract_type="sell")
    loans     = contracts.filter(contract_type="loan")
    transfers = contracts.filter(contract_type="transfer")

    return render(request, "vehicles/vehicle_detail.html", {
        "vehicle": vehicle,
        "owner": owner,
        "fines": fines_qs,
        "unpaid_fines": unpaid_fines,
        "paid_fines": paid_fines,
        "status_history": status_history,
        "rentals": rentals,
        "services": services,
        "sales": sales,
        "loans": loans,
        "transfers": transfers,
    })
# =============================
# Modification véhicule
# =============================
class VehicleUpdateView(UpdateView):
    model = Vehicle
    fields = ["plate_number", "serial_number", "vehicle_type", "brand", "model", "status"]
    template_name = "vehicles/add_vehicle.html"
    success_url = reverse_lazy("vehicles:vehicles_list")

    def form_valid(self, form):
        vehicle = form.instance
        # marquer qui a modifié (si tu utilises ce champ ailleurs)
        setattr(vehicle, "_changed_by_user", self.request.user)
        return super().form_valid(form)


# =============================
# Recherche utilisateurs / véhicules
# ============================
def set_related_user(vehicle):
    """
    Détermine l'utilisateur / garage / dealer lié à un véhicule selon son statut.
    Ajoute dynamiquement :
      - vehicle.related_user
      - vehicle.related_role
    """
    vehicle.related_user = None
    vehicle.related_role = None

    status = getattr(vehicle, "status", None)

    # ==========================
    # LOCATION
    # ==========================
    if status == "rented" and hasattr(vehicle, "rentals"):
        r = vehicle.rentals.order_by("-start_date").first()
        if r:
            vehicle.related_user = r.new_user or getattr(r, "renter_user", None)
            vehicle.related_role = "Loué à"

    # ==========================
    # ACHAT / VENTE
    # ==========================
    elif status in ("bought", "sold") and hasattr(vehicle, "contracts"):
        c = vehicle.contracts.order_by("-created_at").first()
        if c:
            vehicle.related_user = c.new_user
            vehicle.related_role = "Acheté par" if status == "bought" else "Vendu à"

    # ==========================
    # PRÊT
    # ==========================
    elif status == "loaned" and hasattr(vehicle, "loans"):
        ln = vehicle.loans.order_by("-start_at").first()
        if ln:
            vehicle.related_user = ln.new_user
            vehicle.related_role = "Prêté à"

    # ==========================
    # MAINTENANCE / GARAGE
    # ==========================
    elif status == "maintenance" and hasattr(vehicle, "mechanic_services"):
        svc = vehicle.mechanic_services.order_by("-date").first()
        if svc:
            garage = getattr(svc, "garage", None)
            if garage:
                vehicle.related_user = (
                    getattr(garage, "owner", None)
                    or getattr(garage, "external_user", None)
                )
                vehicle.related_role = "En réparation chez garage"
            else:
                mechanic = getattr(svc, "mechanic", None) or getattr(svc, "external_mechanic", None)
                vehicle.related_user = getattr(mechanic, "user", None) or mechanic
                vehicle.related_role = "En réparation"

    # ==========================
    # DEALER
    # ==========================
    elif status in ("dealer_sold", "dealer_transfer"):
        dealer = getattr(vehicle, "dealer", None)
        if dealer:
            vehicle.related_user = (
                getattr(dealer, "user", None)
                or getattr(dealer, "external_user", None)
            )
            vehicle.related_role = "Dealer"

    # ==========================
    # FALLBACK PROPRIÉTAIRE
    # ==========================
    if vehicle.related_user is None and getattr(vehicle, "owner", None):
        vehicle.related_user = vehicle.owner
        vehicle.related_role = "Propriétaire"

    return vehicle

@login_required
def search_results(request):
    query = request.GET.get("query", "").strip()
    user_page = request.GET.get("user_page", 1)
    vehicle_page = request.GET.get("vehicle_page", 1)

    if not query:
        return render(request, "vehicles/search_results.html", {
            "query": query,
            "matched_users": [],
            "matched_vehicles": [],
            "show_user_with_vehicles": False,
        })

    #  Filtrer utilisateurs
    user_filter = (
        Q(simple__first_name__icontains=query) |
        Q(simple__last_name__icontains=query) |
        Q(businessprofile__business_name__icontains=query) |
        Q(businessprofile__patente_number__icontains=query) |
        Q(email__icontains=query) |
        Q(phone__icontains=query) |
        Q(simple__driver_license_number__icontains=query)  # si driver stored in SimpleProfile
    )

    # mots-clés spéciaux
    if query.lower() in ["staff", "mecanicien", "mécanicien", "mechanic"]:
        if query.lower() == "staff":
            user_filter |= Q(is_staff=True)
        else:
            user_filter |= Q(is_mechanic=True)

    matched_users_qs = CustomUser.objects.filter(user_filter).prefetch_related("owned_vehicles", "fines_received")

    #  Filtrer véhicules
    vehicle_filter = (
        Q(plate_number__icontains=query) |
        Q(serial_number__icontains=query) |
        Q(owner__simple__first_name__icontains=query) |
        Q(owner__simple__last_name__icontains=query) |
        Q(owner__businessprofile__business_name__icontains=query) |
        Q(owner__businessprofile__patente_number__icontains=query) |
        Q(owner__email__icontains=query) |
        Q(owner__simple__driver_license_number__icontains=query)
    )

    matched_vehicles_qs = Vehicle.objects.filter(vehicle_filter).select_related("owner").prefetch_related(
        "contracts", "documents", "fines"
    )

    # Inclure véhicules appartenant aux utilisateurs trouvés
    vehicles_from_users = Vehicle.objects.filter(owner__in=matched_users_qs)
    all_vehicles_qs = (matched_vehicles_qs | vehicles_from_users).distinct()

    #  Pagination
    users_page = Paginator(matched_users_qs, 3).get_page(user_page)
    vehicles_page = Paginator(all_vehicles_qs, 3).get_page(vehicle_page)

    #  Ajouter infos véhicules et related_user aux utilisateurs
    for u in users_page:
    # Véhicules possédés
        owned = getattr(u, "owned_vehicles", None)
        u.vehicles_list = (
        [set_related_user(v) for v in owned.all()]
            if owned is not None
            else []
    )

    # Contraventions impayées
        fines = getattr(u, "fines_received", None)
        u.unpaid_fines = fines.filter(is_paid=False) if fines is not None else []

    #  Ajouter related_user aux véhicules indépendants
    vehicles_page.object_list = [set_related_user(v) for v in vehicles_page.object_list]

    return render(request, "vehicles/search_results.html", {
        "query": query,
        "matched_users": users_page,
        "matched_vehicles": vehicles_page,
        "show_user_with_vehicles": matched_users_qs.exists(),
    })


# =============================
# VehicleStatusHistory - Historique des statuts
# =============================
@login_required
def vehicle_status_history_list(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)
    histories = VehicleStatusHistory.objects.filter(vehicle=vehicle).order_by('-changed_at')
    return render(request, 'vehicles/vehicle_status_history_list.html', {
        'vehicle': vehicle,
        'histories': histories
    })


@login_required
def vehicle_status_history_add(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)
    if request.method == 'POST':
        form = VehicleStatusHistoryForm(request.POST)
        if form.is_valid():
            history = form.save(commit=False)
            history.vehicle = vehicle
            history.changed_by = request.user if hasattr(history, "changed_by") else None
            history.save()
            messages.success(request, "Historique ajoutée avec succès !")
            return redirect('vehicles:vehicle_status_history_list', vehicle_id=vehicle.id)
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    else:
        form = VehicleStatusHistoryForm()
    return render(request, 'vehicles/vehicle_status_history_form.html', {'form': form, 'vehicle': vehicle})


@login_required
def vehicle_status_history_detail(request, history_id):
    history = get_object_or_404(VehicleStatusHistory, id=history_id, vehicle__owner=request.user)
    return render(request, 'vehicles/vehicle_status_history_detail.html', {'history': history})


@login_required
def vehicle_status_history_delete(request, history_id):
    history = get_object_or_404(VehicleStatusHistory, id=history_id, vehicle__owner=request.user)
    vehicle = history.vehicle
    if request.method == 'POST':
        history.delete()
        messages.success(request, "Historique supprimée avec succès !")
        return redirect('vehicles:vehicle_status_history_list', vehicle_id=vehicle.id)
    return render(request, 'vehicles/vehicle_status_history_confirm_delete.html', {'history': history})
    
from .models import Vehicle
from users.models import SimpleProfile, BusinessProfile

@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def htmx_owner_vehicles(request):
    owner_type = request.GET.get("owner_type")
    owner_id = request.GET.get("owner_id")

    vehicles = Vehicle.objects.none()

    if owner_type == "simple":
        vehicles = Vehicle.objects.filter(owner_simple_id=owner_id)

    elif owner_type == "business":
        vehicles = Vehicle.objects.filter(owner_business_id=owner_id)

    return render(
        request,
        "vehicles/partials/vehicle_select.html",
        {"vehicles": vehicles}
    )