"""
Définition des routes du module api_auth.
Inclut les vues de connexion, déconnexion, inscription et la page d'accueil.
"""

from django.urls import include, path

from .views import (
    CustomLoginView,
    CustomLogoutView,
    RegisterView,
    api_auth_home,
)

urlpatterns = [
    # Page d'accueil du module d'authentification
    path("", api_auth_home, name="api_auth_home"),
    # Route d'inscription
    path("register/", RegisterView.as_view(), name="register"),
    # Route de connexion personnalisée
    path("login/", CustomLoginView.as_view(), name="login"),
    # Route de déconnexion avec redirection vers /api-auth/login/
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    # Interface d'authentification HTML de Django REST Framework
    path("", include("rest_framework.urls")),
]
