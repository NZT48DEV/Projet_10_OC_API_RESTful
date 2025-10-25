"""
Vues principales du module users.
Gèrent la gestion des utilisateurs, leurs droits d’accès et
la consultation du profil personnel (/me/).
"""

from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .permissions import IsNotAuthenticated, IsSelfOrReadOnly
from .serializers import UserDetailSerializer, UserListSerializer


class UserViewSet(viewsets.ModelViewSet):
    """Vue de gestion CRUD pour le modèle utilisateur."""

    queryset = User.objects.all().order_by("id")

    def get_serializer_class(self):
        """Choisit le serializer selon l’action en cours."""
        if self.action == "list":
            return UserListSerializer
        return UserDetailSerializer

    def get_permissions(self):
        """Applique les permissions adaptées à chaque action."""
        if self.action == "create":
            return [IsNotAuthenticated()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSelfOrReadOnly()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """Filtre la liste selon les droits de l’utilisateur."""
        user = self.request.user
        if user.is_superuser:
            return User.objects.all().order_by("id")
        return User.objects.filter(id=user.id).order_by("id")

    def list(self, request, *args, **kwargs):
        """Liste restreinte aux utilisateurs authentifiés."""
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentification requise."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return super().list(request, *args, **kwargs)

    def perform_destroy(self, instance):
        """Empêche la suppression d’autrui sauf pour un superuser."""
        if (
            self.request.user != instance
            and not self.request.user.is_superuser
        ):
            raise PermissionDenied("Action non autorisée.")
        instance.delete()

    def destroy(self, request, *args, **kwargs):
        """Supprime un compte utilisateur avec confirmation HTTP 204."""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            status=status.HTTP_204_NO_CONTENT,
            content_type="application/json",
        )


class MeView(APIView):
    """Vue renvoyant les informations du profil connecté (/me/)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Renvoie les informations du profil utilisateur courant."""
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)
