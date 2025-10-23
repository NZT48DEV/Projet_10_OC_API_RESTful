import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import User


@pytest.mark.django_db
class TestApiAuth:
    """Tests essentiels du module api_auth (inscription, login, logout, JWT)."""

    def setup_method(self):
        """Initialisation par test — DB disponible ici."""
        self.client = APIClient()
        self.user_data = {
            "username": "newuser",
            "password": "StrongPass123!",
            "email": "newuser@example.com",
            "age": 25,
            "can_be_contacted": True,
            "can_data_be_shared": False,
        }
        self.user = User.objects.create_user(
            username="existing",
            password="pass1234",
            age=30,
            can_be_contacted=True,
            can_data_be_shared=False,
        )

    # ---------- REGISTER ----------
    def test_register_creates_user_successfully(self):
        """Vérifie qu’un utilisateur peut s’inscrire correctement."""
        url = reverse("register")
        res = self.client.post(url, self.user_data, format="json")

        assert res.status_code == status.HTTP_201_CREATED
        assert "message" in res.data
        assert "créé" in res.data["message"].lower()
        assert User.objects.filter(username="newuser").exists()

    def test_authenticated_user_cannot_register_again(self):
        """Un utilisateur déjà connecté ne peut pas créer un autre compte."""
        self.client.force_authenticate(user=self.user)
        url = reverse("register")
        res = self.client.post(url, self.user_data, format="json")

        assert res.status_code in [403, 405]
        self.client.logout()

    def test_register_get_returns_help_message(self):
        """Un GET sur /register/ renvoie un message explicatif."""
        url = reverse("register")
        res = self.client.get(url)
        assert res.status_code == 200
        assert "Utilisez POST" in res.data["detail"]

    # ---------- LOGIN / LOGOUT ----------
    def test_login_redirects_authenticated_user(self, client):
        """
        Un utilisateur connecté via session Django
        est redirigé vers /api/.
        """
        # Crée une vraie session de connexion
        client.login(username="existing", password="pass1234")

        url = reverse("login")
        res = client.get(url)

        assert res.status_code == 302
        assert res.url == "/api/"

    def test_login_view_returns_html_for_authenticated_user(self):
        """
        La vue de login retourne la page HTML
        si l'utilisateur n'est pas dans une session Django.
        """
        self.client.force_authenticate(user=self.user)
        url = reverse("login")
        res = self.client.get(url)
        assert res.status_code == 200
        assert b"<form" in res.content

    def test_logout_redirects_to_login(self, rf):
        """La déconnexion redirige toujours vers /api-auth/login/."""
        from api_auth.views import CustomLogoutView

        request = rf.get("/api-auth/logout/")
        request.user = self.user
        response = CustomLogoutView.as_view()(request)
        assert response.status_code == 302
        assert response.url == "/api-auth/login/"

    # ---------- HOMEPAGE ----------
    def test_api_auth_homepage_renders(self, client):
        """La page d’accueil de l’API s’affiche correctement."""
        url = reverse("api_auth_home")
        res = client.get(url)
        assert res.status_code == 200
        assert b"Bienvenue sur l" in res.content

    # ---------- JWT AUTH ----------
    def test_jwt_token_obtain_and_refresh(self):
        """Vérifie l’obtention et le rafraîchissement des tokens JWT."""
        url_obtain = reverse("token_obtain_pair")
        url_refresh = reverse("token_refresh")

        # 1. Obtention d’un token valide
        response = self.client.post(
            url_obtain,
            {"username": "existing", "password": "pass1234"},
            format="json",
        )
        assert response.status_code == 200, f"Réponse: {response.data}"
        assert "access" in response.data and "refresh" in response.data

        refresh_token = response.data["refresh"]

        # 2. Rafraîchissement du token
        response2 = self.client.post(
            url_refresh, {"refresh": refresh_token}, format="json"
        )
        assert response2.status_code == 200
        assert "access" in response2.data

    def test_jwt_token_invalid_credentials(self):
        """Connexion JWT échoue avec de mauvaises informations."""
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url,
            {"username": "existing", "password": "wrongpass"},
            format="json",
        )
        assert response.status_code == 401
        assert "no_active_account" in str(response.data).lower()
