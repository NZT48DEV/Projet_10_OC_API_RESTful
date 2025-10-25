"""
Définition des routes principales du projet SoftDesk.
Regroupe les endpoints d'administration, d'API, d'authentification et OAuth2.
"""

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

urlpatterns = [
    # Interface d’administration Django
    path("admin/", admin.site.urls),
    # Gestion des utilisateurs
    path("api/users/", include("users.urls")),
    # API principale : projets, issues, commentaires, etc.
    path("api/", include("projects.urls")),
    # Authentification personnalisée : login, register, logout
    path("api-auth/", include("api_auth.urls")),
    # OAuth2 Provider : token, refresh, revoke, introspect
    path("o/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    # Redirection par défaut vers la page d’authentification
    path("", lambda request: redirect("/api-auth/")),
]
