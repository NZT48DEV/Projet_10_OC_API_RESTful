from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from .models import User
from .permissions import IsNotAuthenticated, IsSelfOrReadOnly
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    (Documentation interne)
    Gère les opérations CRUD sur les utilisateurs.
    """

    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        user = self.request.user
        # 🔐 L'utilisateur ne voit que son propre compte.
        # Les autres IDs (même existants) renverront 404 pour éviter toute
        # fuite.
        if user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=user.id)

    def get_permissions(self):
        # Création autorisée uniquement pour les utilisateurs non connectés.
        if self.action == "create":
            return [IsNotAuthenticated()]
        # Modification / suppression → réservé à soi-même.
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSelfOrReadOnly()]
        # Lecture → nécessite d’être authentifié.
        return [IsAuthenticated()]

    def perform_destroy(self, instance):
        """
        Supprime uniquement si l'utilisateur supprime son propre compte.
        Renvoie 404 pour toute tentative de suppression d'un autre utilisateur.
        """
        if (
            self.request.user != instance
            and not self.request.user.is_superuser
        ):
            # Même stratégie : on ne révèle pas si l'utilisateur cible existe.
            raise PermissionDenied("Action non autorisée.")
        instance.delete()
