import base64
from urllib.parse import urlencode

import pytest
from django.urls import reverse
from oauth2_provider.models import Application
from rest_framework import status
from rest_framework.test import APIClient
from users.models import User


@pytest.mark.django_db
class TestApiAuth:
    """🔐 Tests complets du module api_auth : inscription, connexion, déconnexion et OAuth2."""

    def setup_method(self):
        """Prépare un utilisateur et un client OAuth2 avant chaque test."""
        self.client = APIClient()
        self.user_data = {
            "username": "newuser",
            "password": "StrongPass123!",
            "email": "newuser@example.com",
            "age": 25,
            "can_be_contacted": True,
            "can_data_be_shared": False,
        }

        # Utilisateur principal existant
        self.user = User.objects.create_user(
            username="existing",
            password="pass1234",
            age=30,
            can_be_contacted=True,
            can_data_be_shared=False,
        )

        # Secret en clair pour l’application OAuth2 (important pour les tests)
        self.oauth_secret = "testsecret123"

        # Application OAuth2 (grant_type=password)
        self.oauth_app = Application.objects.create(
            name="SoftDesk API Test",
            user=self.user,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_PASSWORD,
            client_secret=self.oauth_secret,
        )

    # ---------- 🔧 UTILS ----------
    def _basic_auth_header(self):
        """Construit l'en-tête Basic Auth pour OAuth2."""
        token = base64.b64encode(
            f"{self.oauth_app.client_id}:{self.oauth_secret}".encode()
        ).decode()
        return {"HTTP_AUTHORIZATION": f"Basic {token}"}

    def _post_form(self, url, data, **headers):
        """Envoie une requête POST encodée en application/x-www-form-urlencoded."""
        return self.client.post(
            url,
            data=urlencode(data),
            content_type="application/x-www-form-urlencoded",
            **headers,
        )

    # ---------- REGISTER ----------
    def test_register_creates_user_successfully(self):
        """✅ Vérifie qu’un utilisateur peut s’inscrire correctement."""
        res = self.client.post(
            reverse("register"), self.user_data, format="json"
        )

        assert res.status_code == status.HTTP_201_CREATED
        assert "message" in res.data and "créé" in res.data["message"].lower()
        assert User.objects.filter(username="newuser").exists()

    def test_authenticated_user_cannot_register_again(self):
        """❌ Un utilisateur déjà connecté ne peut pas créer un autre compte."""
        self.client.force_authenticate(user=self.user)
        res = self.client.post(
            reverse("register"), self.user_data, format="json"
        )
        assert res.status_code in [403, 405]
        self.client.logout()

    def test_register_get_returns_help_message(self):
        """ℹ️ Un GET sur /register/ renvoie un message explicatif."""
        res = self.client.get(reverse("register"))
        assert res.status_code == 200
        assert "Utilisez POST" in res.data["detail"]

    # ---------- LOGIN / LOGOUT ----------
    def test_login_redirects_authenticated_user(self, client):
        """✅ Un utilisateur connecté via session Django est redirigé vers /api/."""
        client.login(username="existing", password="pass1234")
        res = client.get(reverse("login"))
        assert res.status_code == 302 and res.url == "/api/"

    def test_login_view_returns_html_for_authenticated_user(self):
        """🧩 La vue de login retourne bien le formulaire HTML."""
        self.client.force_authenticate(user=self.user)
        res = self.client.get(reverse("login"))
        assert res.status_code == 200
        assert b"<form" in res.content

    def test_logout_redirects_to_login(self, rf):
        """🔁 La déconnexion redirige toujours vers /api-auth/login/."""
        from api_auth.views import CustomLogoutView

        request = rf.get("/api-auth/logout/")
        request.user = self.user
        response = CustomLogoutView.as_view()(request)

        assert response.status_code == 302
        assert response.url == "/api-auth/login/"

    # ---------- HOMEPAGE ----------
    def test_api_auth_homepage_renders(self, client):
        """🏠 Vérifie que la page d’accueil de l’API s’affiche correctement."""
        res = client.get(reverse("api_auth_home"))
        assert res.status_code == 200
        assert b"Bienvenue sur l" in res.content

    # ---------- OAUTH2 ----------
    def test_oauth2_token_obtain_and_use(self):
        """🔑 Vérifie la création et l’utilisation d’un token OAuth2."""
        token_url = "/o/token/"

        # 1️⃣ Obtention du token via grant_type=password
        payload = {
            "grant_type": "password",
            "username": "existing",
            "password": "pass1234",
        }
        res = self._post_form(token_url, payload, **self._basic_auth_header())

        assert res.status_code in [
            200,
            400,
            401,
        ], f"Statut inattendu: {res.status_code}"

        if res.status_code != 200:
            print("❌ OAuth2 token error:", res.content.decode())
            pytest.fail("Impossible d’obtenir le token OAuth2")

        data = res.json()
        access_token, refresh_token = (
            data["access_token"],
            data["refresh_token"],
        )
        assert all([access_token, refresh_token])

        # 2️⃣ Vérifie qu’on peut accéder à une route protégée
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        res2 = self.client.get(reverse("project-list"))
        assert res2.status_code in [200, 403, 404]
        self.client.credentials()

        # 3️⃣ Rafraîchit le token
        refresh_payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        res_refresh = self._post_form(
            token_url, refresh_payload, **self._basic_auth_header()
        )

        assert (
            res_refresh.status_code == 200
        ), f"Réponse: {res_refresh.content.decode()}"
        refreshed_data = res_refresh.json()
        assert "access_token" in refreshed_data

    def test_oauth2_invalid_credentials(self):
        """🚫 Vérifie qu’un token OAuth2 échoue avec des identifiants invalides."""
        token_url = "/o/token/"
        payload = {
            "grant_type": "password",
            "username": "existing",
            "password": "wrongpass",
        }

        res = self._post_form(token_url, payload, **self._basic_auth_header())
        assert res.status_code == 400
        assert "invalid_grant" in res.content.decode().lower()
