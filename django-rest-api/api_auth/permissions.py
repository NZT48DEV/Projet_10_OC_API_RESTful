from rest_framework import permissions


class IsNotAuthenticated(permissions.BasePermission):
    """Empêche les utilisateurs connectés de créer un autre compte."""

    def has_permission(self, request, view):
        # Autoriser seulement si l'utilisateur n'est pas connecté
        return not request.user or not request.user.is_authenticated
