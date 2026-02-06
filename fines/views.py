from decimal import Decimal
import csv

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse
from django.db import models
from users.decorators import verified_required
from .models import Fine, DeletedFine
from payments.models import Balance, Transaction, Payment
from django.contrib.auth.models import User

from .forms import FineForm
from .serializers import FineSerializer
from .permissions import IsOwnerOrAdmin

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

# from .utils import send_payment_notification  # ⚠️ Décommente si utilitaire existant


# === Helpers ===
def user_can_access_fine(user, fine):
    """Vérifie si l’utilisateur peut accéder à une amende"""
    return user.is_staff or user == fine.driver


# === EXPORT CSV ===
@user_passes_test(lambda u: u.is_superuser)
def export_deleted_fines_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="amendes_supprimees.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'ID original', 'Propriétaire', 'Conducteur', 'Montant', 'Raison',
        'Supprimée par', 'Motif de suppression', 'Date de suppression'
    ])
    for fine in DeletedFine.objects.all():
        writer.writerow([
            fine.original_id,
            fine.owner,     # propriétaire
            getattr(fine, "driver", ""),  # conducteur si présent
            fine.amount,
            fine.reason,
            fine.deleted_by,
            fine.delete_reason,
            fine.deleted_at.strftime('%Y-%m-%d %H:%M') if fine.deleted_at else ""
        ])
    return response


# === VUES HTML ===

@login_required
@verified_required
def fine_list(request):
    query = request.GET.get('query', '').strip()

    if request.user.is_staff:
        fines = Fine.objects.all()
    else:
        # ⚠️ Désormais seul le driver peut voir ses amendes
        fines = Fine.objects.filter(driver=request.user)

    if query:
        fines = fines.filter(
            models.Q(reason__icontains=query) |
            models.Q(vehicle__plate_number__icontains=query) |
            models.Q(driver__email__icontains=query) |
            models.Q(driver__last_name__icontains=query) |
            models.Q(driver__first_name__icontains=query) |
            models.Q(fine_id__icontains=query) |
            models.Q(driver__driver_license__icontains=query)
        )

    return render(request, 'fines/fine_list.html', {'fines': fines, 'query': query})

@verified_required
@login_required
def fine_detail(request, fine_id):
    fine = get_object_or_404(Fine, id=fine_id)
    if not user_can_access_fine(request.user, fine):
        return JsonResponse({'error': "Accès refusé"}, status=403)
    return render(request, 'fines/fine_detail.html', {'fine': fine})
@verified_required
@login_required
def unpaid_fines_view(request):
    # ⚠️ On suppose que seuls les conducteurs voient leurs propres amendes non payées
    fines = Fine.objects.filter(driver=request.user, is_paid=False)

    # On ne garde que les fine_id
    fine_ids = fines.values_list('fine_id', flat=True)

    return render(request, "fines/unpaid_fines.html", {"fine_ids": fine_ids})

@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def fine_create(request):
    if request.method == "POST":
        form = FineForm(request.POST)

        if form.is_valid():
            fine = form.save(commit=False)

            # 🔐 Sécurité : le véhicule doit appartenir au propriétaire
            if fine.vehicle.owner != fine.owner:
                form.add_error(
                    "vehicle",
                    "Ce véhicule n'appartient pas au propriétaire sélectionné."
                )
            else:
                fine.issuer = request.user
                fine.save()
                return redirect("fines:fine_detail", fine_id=fine.id)

    else:
        form = FineForm()

    return render(request, "fines/fine_create.html", {"form": form})

@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def fine_update(request, fine_id):
    fine = get_object_or_404(Fine, id=fine_id)
    if request.method == 'POST':
        form = FineForm(request.POST, instance=fine)
        reason = request.POST.get('reason', '').strip()
        if not reason:
            return JsonResponse({'error': 'Une raison est requise pour modifier une amende.'}, status=400)
        if form.is_valid():
            form.save()
            return redirect('fines:fine_detail', fine_id=fine.id)
    else:
        form = FineForm(instance=fine)
    return render(request, 'fines/fine_form.html', {'form': form, 'fine': fine})


@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def fine_delete(request, fine_id):
    fine = get_object_or_404(Fine, id=fine_id)
    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        if not reason:
            return JsonResponse({'error': 'Une raison est requise pour supprimer cette amende.'}, status=400)
        DeletedFine.objects.create(
            original_id=fine.id,
            owner=fine.owner,       # propriétaire
            driver=fine.driver,   # conducteur
            amount=fine.amount,
            reason=fine.reason,
            deleted_by=request.user,
            delete_reason=reason
        )
        fine.delete()
        return redirect('fines:fine_list')
    return render(request, 'fines/fine_confirm_delete.html', {'fine': fine})

from payments.services.payment_service import PaymentService
from django.core.exceptions import ValidationError


@verified_required
@login_required
def fine_pay(request, fine_id):
    fine = get_object_or_404(Fine, id=fine_id)

    if not user_can_access_fine(request.user, fine):
        messages.error(request, "Accès refusé.")
        return redirect("fines:fine_list")

    if fine.is_paid:
        messages.info(request, "Cette amende est déjà payée.")
        return redirect("payments:payment_list")

    if request.method == "POST":
        try:
            PaymentService.pay_fine(
                user=request.user,
                fine=fine
            )
            messages.success(request, "Amende payée avec succès.")
            return redirect("payments:payment_list")

        except ValidationError as e:
            messages.error(request, str(e))

    return render(
        request,
        "fines/fine_pay_form.html",
        {"fine": fine}
    )
    
from users.models import SimpleProfile

@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def htmx_driver_lookup(request):
    driver_license_number = request.GET.get("driver_license_number", "").strip()

    profile = None
    if driver_license_number:
        profile = SimpleProfile.objects.filter(
            driver_license_number__iexact=driver_license_number
        ).select_related("user").first()

    return render(
        request,
        "fines/partials/driver_result.html",
        {
            "profile": profile,
            "query": driver_license_number,
        }
    )
    
from django.db.models import Q
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render as django_render
from users.models import SimpleProfile, BusinessProfile


@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def htmx_owner_lookup(request):
    query = request.GET.get("owner_query", "").strip()

    simple_results = SimpleProfile.objects.none()
    business_results = BusinessProfile.objects.none()

    if query:
        # 🔹 Utilisateurs simples (via User)
        simple_results = (
            SimpleProfile.objects
            .select_related("user")
            .filter(
                Q(user__simple__first_name__icontains=query) |
                Q(user__simple__last_name__icontains=query)
            )
        )

        # 🔹 Entreprises
        business_results = BusinessProfile.objects.filter(
            business_name__icontains=query
        )

    return django_render(
        request,
        "fines/partials/owner_result.html",
        {
            "query": query,
            "simple_results": simple_results,
            "business_results": business_results,
        }
    )