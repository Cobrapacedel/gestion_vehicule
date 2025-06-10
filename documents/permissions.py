from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Seuls les administrateurs ou l'utilisateur concerné peuvent voir et payer leurs amendes.
    """

    def has_permission(self, request, view):
        if request.user.is_staff or request.user.is_superuser:
            return True  # Les admins ont tous les droits
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff  # Seul le propriétaire ou un admin peut accéder