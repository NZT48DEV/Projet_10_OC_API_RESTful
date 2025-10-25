"""
Définition des permissions personnalisées pour le module users.
Gère les accès aux comptes utilisateurs et les restrictions RGPD.
"""

from rest_framework import permissions


class IsSelfOrReadOnly(permissions.BasePermission):
    """
    Autorise la lecture pour tous les utilisateurs connectés.
    La modification ou la suppression n’est possible que sur
    son propre compte utilisateur.
    """

    def has_object_permission(self, request, view, obj):
        """Vérifie les droits de lecture ou d’auto-modification."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user


class IsNotAuthenticated(permissions.BasePermission):
    """
    Interdit aux utilisateurs connectés de créer un nouveau compte.
    """

    def has_permission(self, request, view):
        """Autorise uniquement les utilisateurs non authentifiés."""
        return not request.user or not request.user.is_authenticated
