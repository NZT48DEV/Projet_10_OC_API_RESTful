from django.urls import include, path

from .views import (
    CustomLoginView,
    CustomLogoutView,
    RegisterView,
    api_auth_home,
)

urlpatterns = [
    # Page d'accueil
    path("", api_auth_home, name="api_auth_home"),
    # Inscription
    path("register/", RegisterView.as_view(), name="register"),
    # Connexion personnalisée
    path("login/", CustomLoginView.as_view(), name="login"),
    # Déconnexion avec redirection vers /api-auth/login/
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    # Interface DRF classique (login/logout HTML)
    path("", include("rest_framework.urls")),
]
