"""
Vues du module api_auth.
Gère l'inscription, la connexion, la déconnexion et la page d'accueil.
"""

from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from rest_framework import generics, status
from rest_framework.response import Response
from users.models import User
from users.serializers import UserDetailSerializer

from .permissions import IsNotAuthenticated


class RegisterView(generics.CreateAPIView):
    """
    Permet à un utilisateur non authentifié de créer un nouveau compte.
    """

    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsNotAuthenticated]

    def get(self, request, *args, **kwargs):
        """Empêche les requêtes GET sur la route d'inscription."""
        return Response(
            {"detail": "Utilisez POST pour créer un nouveau compte."},
            status=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        """Crée un utilisateur et renvoie un message de confirmation."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
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
            headers=headers,
        )


class CustomLoginView(LoginView):
    """
    Vue de connexion personnalisée.
    Redirige l'utilisateur authentifié vers la page principale.
    """

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
    """
    Déconnecte l'utilisateur et redirige vers la page de connexion.
    """

    def dispatch(self, request, *args, **kwargs):
        """Exécute la déconnexion et redirige vers /api-auth/login/."""
        super().dispatch(request, *args, **kwargs)
        return redirect("/api-auth/login/")


def api_auth_home(request):
    """
    Page d'accueil du module api_auth.
    Affiche les liens de connexion et d'inscription.
    """
    return render(request, "api_auth/index.html")
