from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

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
    # JWT
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Interface DRF (login/logout)
    path("", include("rest_framework.urls")),
]
