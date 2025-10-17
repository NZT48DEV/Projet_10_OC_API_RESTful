from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import User
from .permissions import IsSelfOrReadOnly
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD complet sur les utilisateurs
    - Inscription ouverte (AllowAny)
    - Consultation/Modification réservées aux utilisateurs connectés
    - Suppression uniquement autorisée sur son propre compte
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        if self.action == "list":
            return User.objects.filter(id=self.request.user.id)
        return super().get_queryset()

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        elif self.action in ["update", "partial_update", "destroy"]:
            # Authentification obligatoire
            # + vérification qu’il s’agit du bon user
            return [IsAuthenticated(), IsSelfOrReadOnly()]
        return [IsAuthenticated()]

    def perform_destroy(self, instance):
        """
        Supprime uniquement si l'utilisateur supprime son propre compte.
        """
        if self.request.user != instance:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(
                "Vous ne pouvez supprimer que votre propre compte."
            )
        instance.delete()
