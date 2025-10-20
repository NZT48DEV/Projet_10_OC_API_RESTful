from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from users.models import User
from users.serializers import UserSerializer

from .permissions import IsNotAuthenticated


class RegisterView(generics.CreateAPIView):
    """
    Permet à un nouvel utilisateur de s'inscrire.
    Accessible uniquement aux utilisateurs non connectés.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsNotAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Fournit un message d'information au lieu d'une erreur 405.
        """
        return Response(
            {"detail": "Utilisez POST pour créer un nouveau compte."},
            status=status.HTTP_200_OK,
        )


def api_auth_home(request):
    """
    Page d'accueil de l'API : propose login ou inscription.
    """
    return render(request, "api_auth/index.html")
