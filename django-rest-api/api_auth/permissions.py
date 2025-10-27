from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class IsNotAuthenticated(permissions.BasePermission):
    """
    Empêche les utilisateurs connectés de créer un autre compte.
    """

    def has_permission(self, request, view):
        # Si l'utilisateur est connecté → on bloque avec un message explicite
        if request.user and request.user.is_authenticated:
            raise PermissionDenied("Vous êtes déjà connecté.")
        return True
