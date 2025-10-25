"""
Définition des routes du module users.
Expose les endpoints pour la gestion des utilisateurs et du profil
personnel (/me/).
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MeView, UserViewSet

router = DefaultRouter()
router.register(r"", UserViewSet, basename="user")

urlpatterns = [
    path("me/", MeView.as_view(), name="me"),
    path("", include(router.urls)),
]
