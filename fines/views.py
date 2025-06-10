from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Fine, FinePay, DeletedFine
from payments.models import Balance
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from .forms import FineForm, FinePayForm
from .serializers import FineSerializer, FinePaySerializer
from .permissions import IsOwnerOrAdmin
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
import csv

# === EXPORT CSV ===
@user_passes_test(lambda u: u.is_superuser)
def export_deleted_fines_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="amendes_supprimees.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'ID original', 'Utilisateur', 'Montant', 'Raison',
        'Supprimée par', 'Motif de suppression', 'Date de suppression'
    ])
    for fine in DeletedFine.objects.all():
        writer.writerow([
            fine.original_id,
            fine.user,
            fine.amount,
            fine.reason,
            fine.deleted_by,
            fine.delete_reason,
            fine.deleted_at.strftime('%Y-%m-%d %H:%M')
        ])
    return response

# === VUES HTML ===

@login_required
def fine_list(request):
    if request.user.is_staff:
        fines = Fine.objects.all()
    else:
        fines = Fine.objects.filter(user=request.user)
    return render(request, 'fines/fine_list.html', {'fines': fines})

@login_required
def fine_detail(request, fine_id):
    fine = get_object_or_404(Fine, id=fine_id)
    if fine.user != request.user and not request.user.is_staff:
        return JsonResponse({'error': "Accès refusé"}, status=403)
    return render(request, 'fines/fine_detail.html', {'fine': fine})

@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def fine_create(request):
    if request.method == 'POST':
        form = FineForm(request.POST)
        if form.is_valid():
            fine = form.save(commit=False)
            fine.save()
            return redirect('fines:fine_detail', fine_id=fine.id)
    else:
        form = FineForm()
    return render(request, 'fines/fine_create.html', {'form': form})

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
            user=fine.user,
            amount=fine.amount,
            reason=fine.reason,
            deleted_by=request.user,
            delete_reason=reason
        )
        fine.delete()
        return redirect('fines:fine_list')
    return render(request, 'fines/fine_confirm_delete.html', {'fine': fine})

@login_required
def pay_fine(request, fine_id):
    fine = get_object_or_404(Fine, id=fine_id)
    fine.apply_penalty()
    balance, _ = Balance.objects.get_or_create(user=fine.user)
    
    if not fine.is_paid and balance.amount >= fine.amount:
        balance.amount -= fine.amount   
        balance.save()
        fine.is_paid = True
        fine.save()
        return redirect('fines:fine_list')
    if fine.user != request.user and not request.user.is_staff:
        return JsonResponse({'error': "Vous n'avez pas le droit de payer cette amende"}, status=403)
    if request.method == 'POST':
        form = FinePayForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.fine = fine
            payment.user = request.user
            payment.save()
            fine.status = 'paid'
            fine.save()
            return JsonResponse({'message': 'Amende payée avec succès', 'status': 'success'})
    else:
        form = FinePayForm()
    return render(request, 'fines/fine_payment.html', {'form': form, 'fine': fine})

# === API REST (DRF) ===

class FineViewSet(viewsets.ModelViewSet):
    serializer_class = FineSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Fine.objects.all()
        return Fine.objects.filter(user=self.request.user)

class FinePayViewSet(viewsets.ModelViewSet):
    serializer_class = FinePaySerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        if self.request.user.is_staff:
            return FinePay.objects.all()
        return FinePay.objects.filter(user=self.request.user)

@login_required       
def fine_payment_view(request):
    return render(request, 'fines/fine_payment_form.html')