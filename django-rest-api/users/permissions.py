from rest_framework import permissions


class IsSelfOrReadOnly(permissions.BasePermission):
    """
    Permission : un utilisateur ne peut modifier ou supprimer
    que son propre compte. Les autres peuvent seulement le lire.
    """

    def has_object_permission(self, request, view, obj):
        # Lecture autorisée à tous les utilisateurs connectés
        if request.method in permissions.SAFE_METHODS:
            return True
        # Modification / suppression
        # autorisée uniquement si l'utilisateur agit sur lui-même
        return obj == request.user
