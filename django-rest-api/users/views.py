from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from .models import User
from .permissions import IsNotAuthenticated, IsSelfOrReadOnly
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    VueSet gérant les opérations CRUD sur les utilisateurs.

    Fonctionnalités :
    - Création de compte ouverte à tous (users non authentifiés uniquement).
    - Consultation et modification réservées aux utilisateurs connectés.
    - Chaque utilisateur ne peut consulter ou modifier que son propre compte.
    - Les administrateurs (superusers) ont accès à tous les utilisateurs.
    - Suppression autorisée uniquement par l’utilisateur sur son propre compte.
    """

    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return User.objects.all()

        if user.is_authenticated:
            return User.objects.all()

        return User.objects.none()

    def get_permissions(self):
        if self.action == "create":
            # Empêche la création de compte si déjà connecté
            return [IsNotAuthenticated()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSelfOrReadOnly()]
        return [IsAuthenticated()]

    def perform_destroy(self, instance):
        """
        Supprime uniquement si l'utilisateur supprime son propre compte.
        """
        if self.request.user != instance:
            raise PermissionDenied(
                "Vous ne pouvez supprimer que votre propre compte."
            )
        instance.delete()
