from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
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
        return Response(
            {"detail": "Utilisez POST pour créer un nouveau compte."},
            status=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        user = serializer.instance
        return Response(
            {
                "message": (
                    f"✅ Le compte utilisateur '{user.username}' "
                    "a été créé avec succès !"
                ),
                "user": serializer.data,
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class CustomLoginView(LoginView):
    template_name = "rest_framework/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return "/api/"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("/api/")
        return super().get(request, *args, **kwargs)


class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        super().dispatch(request, *args, **kwargs)
        return redirect("/api-auth/login/")


def api_auth_home(request):
    """
    Page d'accueil de l'API : propose login ou inscription.
    """
    return render(request, "api_auth/index.html")
