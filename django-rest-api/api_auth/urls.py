from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import RegisterView, api_auth_home

urlpatterns = [
    # Page d'accueil d'authentification
    path("", api_auth_home, name="api_auth_home"),
    # Inscription
    path("register/", RegisterView.as_view(), name="register"),
    # Authentification JWT
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Authentification par session (interface DRF)
    path("", include("rest_framework.urls")),
]
