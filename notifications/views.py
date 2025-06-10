from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification

@login_required
def notification_list(request):
    """ Affiche la liste des notifications de l'utilisateur connecté """
    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")
    
    context = {
        "notifications": notifications,
    }
    return render(request, "notifications/notification_list.html", context)
    
@login_required
def mark_notification_as_read(request, notification_id):
    """ Marque une notification spécifique comme lue """
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    return JsonResponse({"success": True, "message": "Notification marquée comme lue."})
    
@login_required
def delete_notification(request, notification_id):
    """ Supprime une notification spécifique """
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    return JsonResponse({"success": True, "message": "Notification supprimée."})