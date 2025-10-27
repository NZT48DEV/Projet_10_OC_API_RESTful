"""
Vues du module api_auth.
Gère l'inscription, la connexion, la déconnexion et la page d'accueil.
"""

from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from users.serializers import UserDetailSerializer

from .permissions import IsNotAuthenticated
from .schema_docs import register_get_schema, register_post_schema


class RegisterView(APIView):
    """
    Permet à un utilisateur non authentifié de créer un nouveau compte.
    """

    permission_classes = [IsNotAuthenticated]

    @extend_schema(**register_get_schema)
    def get(self, request, *args, **kwargs):
        """Empêche les requêtes GET sur la route d'inscription."""
        return Response(
            {"detail": "Utilisez POST pour créer un nouveau compte."},
            status=status.HTTP_200_OK,
        )

    @extend_schema(**register_post_schema)
    def post(self, request, *args, **kwargs):
        """Crée un utilisateur et renvoie un message de confirmation."""
        serializer = UserDetailSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Crée l’utilisateur
        serializer.save()
        user = serializer.instance

        return Response(
            {
                "message": (
                    f"Le compte utilisateur '{user.username}' "
                    "a été créé avec succès."
                ),
                "user": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class CustomLoginView(LoginView):
    """Vue de connexion personnalisée."""

    template_name = "rest_framework/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        """Retourne l'URL de redirection après connexion."""
        return "/api/"

    def get(self, request, *args, **kwargs):
        """Redirige un utilisateur déjà connecté vers /api/."""
        if request.user.is_authenticated:
            return redirect("/api/")
        return super().get(request, *args, **kwargs)


class CustomLogoutView(LogoutView):
    """Déconnecte l'utilisateur et redirige vers la page de connexion."""

    def dispatch(self, request, *args, **kwargs):
        """Exécute la déconnexion et redirige vers /api-auth/login/."""
        super().dispatch(request, *args, **kwargs)
        return redirect("/api-auth/login/")


def api_auth_home(request):
    """Page d'accueil du module api_auth."""
    return render(request, "api_auth/index.html")
