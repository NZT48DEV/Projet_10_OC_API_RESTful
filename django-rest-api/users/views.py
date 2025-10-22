from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import User
from .permissions import IsNotAuthenticated, IsSelfOrReadOnly
from .serializers import UserDetailSerializer, UserListSerializer


class UserViewSet(viewsets.ModelViewSet):
    """Gère les opérations CRUD sur les utilisateurs."""

    queryset = User.objects.all().order_by("id")

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        return UserDetailSerializer

    def get_permissions(self):
        if self.action == "create":
            return [IsNotAuthenticated()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSelfOrReadOnly()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return User.objects.all().order_by("id")
        return User.objects.filter(id=user.id).order_by("id")

    def list(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentification requise."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return super().list(request, *args, **kwargs)

    def perform_destroy(self, instance):
        if (
            self.request.user != instance
            and not self.request.user.is_superuser
        ):
            raise PermissionDenied("Action non autorisée.")
        instance.delete()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            status=status.HTTP_204_NO_CONTENT, content_type="application/json"
        )
