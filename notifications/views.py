from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Notification
from users.decorators import verified_required

# --- Helpers ---
def user_can_access_notification(user, notification):
    """Vérifie si l’utilisateur peut accéder à une notification"""
    return user.is_staff or user == notification.user
 
# --- Liste des notifications ---
@login_required
@verified_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    # Pagination optionnelle si tu veux
    return render(request, 'notifications/notification_list.html', {'notifications': notifications})

# --- Détail d'une notification ---
@login_required
@verified_required
def notification_detail(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    if not user_can_access_notification(request.user, notification):
        messages.error(request, "Vous n'avez pas le droit de voir cette notification.")
        return redirect('notifications:list')
    return render(request, 'notifications/notification_detail.html', {'notification': notification})

# --- Marquer comme lu ---
@login_required
@verified_required
def notification_mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    if request.method == "POST":
        notification.is_read = True
        notification.save()
        messages.success(request, "Notification marquée comme lue.")
        return redirect('notifications:notification_list')
    return render(request, "notifications/mark_as_read.html", {"notification": notification})

# --- Supprimer une notification ---
@login_required
@verified_required
def notification_delete(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    if not user_can_access_notification(request.user, notification):
        messages.error(request, "Vous n'avez pas le droit de supprimer cette notification.")
        return redirect('notifications:notification_list')

    if request.method == 'POST':
        notification.delete()
        messages.success(request, "Notification supprimée avec succès.")
        return redirect('notifications:notification_list')

    return render(request, 'notifications/notification_delete.html', {'notification': notification})
