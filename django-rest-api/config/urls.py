"""
Définition des routes principales du projet SoftDesk.
Regroupe les endpoints d'administration, d'API, d'authentification, OAuth2 et documentation.
"""

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

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
    # Documentation OpenAPI & interfaces Swagger / ReDoc
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    # Redirection par défaut vers la page d’authentification
    path("", lambda request: redirect("/api-auth/")),
]
