from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

urlpatterns = [
    # Interface d’administration
    path("admin/", admin.site.urls),
    # Gestion des utilisateurs
    path("api/users/", include("users.urls")),
    # API principale (projets, issues, etc.)
    path("api/", include("projects.urls")),
    # Authentification personnalisée (login/register)
    path("api-auth/", include("api_auth.urls")),
    # OAuth2 Provider (tokens, refresh, revoke, etc.)
    path("o/", include("oauth2_provider.urls", namespace="oauth2_provider")),
    # Redirection par défaut vers l’espace d’authentification
    path("", lambda request: redirect("/api-auth/")),
]
