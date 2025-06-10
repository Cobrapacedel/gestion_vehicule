from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q
import json
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .forms import VehicleForm, TransferVehicleForm
from .models import Vehicle, VehicleTransfer
from users.models import CustomUser
from fines.models import Fine
from django.conf import settings
from django.contrib.auth import get_user_model
from . import utils  # Utilisation du fichier utils.py pour les marques/modèles

CustomUser = get_user_model()

from django.http import JsonResponse
from .utils import VEHICLE_DATA  # Dictionnaire avec type -> marques -> modèles

def get_brands(request):
    vehicle_type = request.GET.get("vehicle_type")
    brands = list(VEHICLE_DATA.get(vehicle_type, {}).keys())
    return JsonResponse({"brands": brands})

def get_models(request):
    vehicle_type = request.GET.get("vehicle_type")
    brand = request.GET.get("brand")
    models = VEHICLE_DATA.get(vehicle_type, {}).get(brand, [])
    return JsonResponse({"models": models})

# Vue pour afficher les détails d'un véhicule spécifique
@login_required
def vehicle_status(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    if vehicle.owner != request.user:
        messages.error(request, _("Vous n'êtes pas autorisé à accéder à ce véhicule."))
        return redirect("vehicles:vehicles_list")

    return render(request, "vehicles/vehicle_status.html", {"vehicle": vehicle})

# Vue de recherche des véhicules et des utilisateurs
def search_results(request):
    query = request.GET.get("query", "").strip()

    user_page = request.GET.get("user_page", 1)
    vehicle_page = request.GET.get("vehicle_page", 1)

    # Recherche par utilisateur (nom, prénom, email, téléphone, permis)
    user_filter = Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query) | Q(phone_number__icontains=query) | Q(driver_license__icontains=query)
    matched_users_qs = CustomUser.objects.filter(user_filter).prefetch_related("vehicles", "fines")

    paginator_users = Paginator(matched_users_qs, 3)
    users = paginator_users.get_page(user_page)

    # Recherche par véhicule (plaque, numéro série ou permis propriétaire)
    vehicle_filter = Q(plate_number__icontains=query) | Q(serial_number__icontains=query) | Q(owner__driver_license__icontains=query)
    matched_vehicles_qs = Vehicle.objects.filter(vehicle_filter).select_related("owner").prefetch_related("fines")

    paginator_vehicles = Paginator(matched_vehicles_qs, 3)
    vehicles = paginator_vehicles.get_page(vehicle_page)

    # Détection si l'utilisateur correspond (pour afficher avec ses véhicules et amendes)
    show_user_with_vehicles = matched_users_qs.exists()

    # Ajouter les données à chaque utilisateur trouvé
    for user in users:
        user.vehicles_list = user.vehicles.all()
        user.unpaid_fines = user.fines.filter(paid=False)

    context = {
        "query": query,
        "users": users,
        "vehicles": vehicles,
        "matched_users": users,
        "matched_vehicles": vehicles,
        "show_user_with_vehicles": show_user_with_vehicles,
    }

    return render(request, "vehicles/search_results.html", context)

# Vue pour afficher tous les véhicules de l'utilisateur connecté
@login_required
def vehicles_list(request):
    vehicles = Vehicle.objects.filter(owner=request.user).order_by("-id")

    paginator = Paginator(vehicles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "vehicles/vehicles_list.html", {"vehicles": page_obj})

# Vue pour transférer un véhicule à un autre utilisateur
@login_required
def transfer_vehicle(request):
    if request.method == "POST":
        form = TransferVehicleForm(request.POST)
        if form.is_valid():
            transfer = form.save(commit=False)
            transfer.previous_owner = request.user

            try:
                vehicle = Vehicle.objects.get(id=transfer.vehicle.id)
            except Vehicle.DoesNotExist:
                messages.error(request, _("Le véhicule spécifié n'existe pas."))
                return redirect("vehicles:transfer_vehicle")

            if vehicle.owner != request.user:
                messages.error(request, _("Vous n'êtes pas le propriétaire de ce véhicule."))
                return redirect("vehicles:transfer_vehicle")

            if transfer.new_owner == request.user:
                messages.error(request, _("Vous ne pouvez pas transférer un véhicule à vous-même."))
                return redirect("vehicles:transfer_vehicle")

            if not CustomUser.objects.filter(id=transfer.new_owner.id).exists():
                messages.error(request, _("L'utilisateur destinataire n'existe pas."))
                return redirect("vehicles:transfer_vehicle")

            vehicle.owner = transfer.new_owner
            vehicle.status = "transferred"
            vehicle.save()
            transfer.save()

            messages.success(request, _("Le transfert du véhicule a été effectué avec succès."))
            return redirect("vehicles:vehicles_list")
    
    form = TransferVehicleForm()
    return render(request, "vehicles/vehicle_transfer.html", {"form": form})

# Vue pour ajouter un véhicule
@login_required
def add_vehicle(request):
    if request.method == "POST":
        print("Form submitted:", request.POST)
        form = VehicleForm(request.POST, request.FILES)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.owner = request.user
            vehicle.status = "available"
            vehicle.date_added = timezone.now()
            vehicle.save()
            print("Véhicule enregistré avec succès :", vehicle)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'id': vehicle.id})
            return redirect('vehicles:vehicles_list')
        else:
            print("Erreurs de formulaire :", form.errors)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'errors': form.errors}, status=400)
    else:
        form = VehicleForm()  # <-- CORRIGÉ ICI

    return render(request, 'vehicles/add_vehicle.html', {'form': form})
# Vue pour afficher les détails d'un véhicule
@login_required
def vehicle_detail(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    if vehicle.owner != request.user:
        messages.error(request, _("Vous n'êtes pas autorisé à accéder à ce véhicule."))
        return redirect("vehicles:vehicles_list")

    fines = Fine.objects.filter(vehicle=vehicle).order_by("-date")
    unpaid_fines = fines.filter(paid=False)
    paid_fines = fines.filter(paid=True)

    context = {
        "vehicle": vehicle,
        "fines": fines,
        "unpaid_fines": unpaid_fines,
        "paid_fines": paid_fines,
    }

    return render(request, "vehicles/vehicle_detail.html", context)