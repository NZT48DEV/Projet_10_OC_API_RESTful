import base64
import json
from urllib.parse import urlencode

import pytest
from django.urls import reverse
from oauth2_provider.models import Application
from rest_framework import status
from rest_framework.test import APIClient
from users.models import User


@pytest.mark.django_db
class TestApiAuth:
    """
    Tests complets du module api_auth : inscription, connexion, déconnexion
    et authentification OAuth2.
    """

    def setup_method(self):
        """Prépare un utilisateur et une application OAuth2 avant chaque test."""
        self.client = APIClient()
        self.user_data = {
            "username": "newuser",
            "password": "StrongPass123!",
            "email": "newuser@example.com",
            "age": 25,
            "can_be_contacted": True,
            "can_data_be_shared": False,
        }

        # Création d'un utilisateur existant
        self.user = User.objects.create_user(
            username="existing",
            password="pass1234",
            age=30,
            can_be_contacted=True,
            can_data_be_shared=False,
        )

        # Secret en clair pour l'application OAuth2 (utilisé dans les tests)
        self.oauth_secret = "testsecret123"

        # Création de l'application OAuth2 (grant_type=password)
        self.oauth_app = Application.objects.create(
            name="SoftDesk API Test",
            user=self.user,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_PASSWORD,
            client_secret=self.oauth_secret,
        )

    # ---------- Méthodes utilitaires ----------

    def _basic_auth_header(self):
        """Construit l'en-tête Basic Auth pour l'application OAuth2."""
        token = base64.b64encode(
            f"{self.oauth_app.client_id}:{self.oauth_secret}".encode()
        ).decode()
        return {"HTTP_AUTHORIZATION": f"Basic {token}"}

    def _post_form(self, url, data, **headers):
        """Envoie une requête POST en x-www-form-urlencoded."""
        return self.client.post(
            url,
            data=urlencode(data),
            content_type="application/x-www-form-urlencoded",
            **headers,
        )

    # ---------- Tests d'inscription ----------

    def test_register_creates_user_successfully(self):
        """Vérifie qu'un utilisateur peut s'inscrire correctement."""
        res = self.client.post(
            reverse("register"), self.user_data, format="json"
        )
        assert res.status_code == status.HTTP_201_CREATED
        assert "message" in res.data and "créé" in res.data["message"].lower()
        assert User.objects.filter(username="newuser").exists()

    def test_register_invalid_data_returns_400(self):
        """Vérifie qu'une inscription invalide renvoie bien une erreur 400."""
        invalid_data = {
            "username": "",
            "email": "not_an_email",
            "password": "",
            "age": 22,
            "can_be_contacted": False,
            "can_data_be_shared": True,
        }
        res = self.client.post(
            reverse("register"), invalid_data, format="json"
        )

        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert "errors" in res.data
        assert "username" in res.data["errors"]
        assert "password" in res.data["errors"]

    def test_authenticated_user_cannot_register_returns_403(self):
        """Empêche un utilisateur déjà connecté de créer un autre compte (403 attendu)."""
        self.client.force_authenticate(user=self.user)
        res = self.client.post(
            reverse("register"), self.user_data, format="json"
        )

        assert res.status_code == status.HTTP_403_FORBIDDEN
        assert "detail" in res.data
        assert "déjà connecté" in res.data["detail"].lower()
        self.client.logout()

    def test_register_get_returns_help_message(self):
        """Un GET sur /register/ renvoie un message d'aide explicatif."""
        res = self.client.get(reverse("register"))
        assert res.status_code == 200
        assert "Utilisez POST" in res.data["detail"]

    # ---------- Tests de documentation OpenAPI ----------

    def test_openapi_register_schema_includes_expected_responses(self):
        """Vérifie que la doc OpenAPI inclut bien les codes 201, 400 et 403 pour /api-auth/register/."""
        schema_url = reverse("schema")
        res = self.client.get(schema_url, HTTP_ACCEPT="application/json")

        content_type = res.headers.get("Content-Type", "")
        assert res.status_code == 200
        assert (
            "openapi" in content_type.lower() or "json" in content_type.lower()
        )

        schema = json.loads(res.content.decode())

        paths = schema.get("paths", {})
        register_path = next(
            (p for p in paths if "api-auth/register" in p), None
        )
        assert (
            register_path
        ), "L'endpoint /api-auth/register/ n'est pas présent dans le schéma OpenAPI."

        post_method = paths[register_path].get("post", {})
        responses = post_method.get("responses", {})

        for code in ("201", "400", "403"):
            assert (
                code in responses
            ), f"Le code {code} est manquant dans la doc OpenAPI pour /api-auth/register/."

    # ---------- Tests de connexion/déconnexion ----------

    def test_login_redirects_authenticated_user(self, client):
        """Un utilisateur connecté est redirigé vers la page principale /api/."""
        client.login(username="existing", password="pass1234")
        res = client.get(reverse("login"))
        assert res.status_code == 302 and res.url == "/api/"

    def test_login_view_returns_html_for_authenticated_user(self):
        """La vue de connexion retourne le formulaire HTML attendu."""
        self.client.force_authenticate(user=self.user)
        res = self.client.get(reverse("login"))
        assert res.status_code == 200
        assert b"<form" in res.content

    def test_logout_redirects_to_login(self, rf):
        """La déconnexion redirige vers /api-auth/login/."""
        from api_auth.views import CustomLogoutView

        request = rf.get("/api-auth/logout/")
        request.user = self.user
        response = CustomLogoutView.as_view()(request)

        assert response.status_code == 302
        assert response.url == "/api-auth/login/"

    # ---------- Tests de la page d'accueil ----------

    def test_api_auth_homepage_renders(self, client):
        """Vérifie que la page d'accueil de l'API est accessible."""
        res = client.get(reverse("api_auth_home"))
        assert res.status_code == 200
        assert b"Bienvenue sur l" in res.content

    # ---------- Tests OAuth2 ----------

    def test_oauth2_token_obtain_and_use(self):
        """Teste l'obtention, l'utilisation et le rafraîchissement d'un token."""
        token_url = "/o/token/"

        # Obtention du token via grant_type=password
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
            print("Erreur OAuth2:", res.content.decode())
            pytest.fail("Impossible d'obtenir le token OAuth2")

        data = res.json()
        access_token, refresh_token = (
            data["access_token"],
            data["refresh_token"],
        )
        assert all([access_token, refresh_token])

        # Vérifie l'accès à une route protégée
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        res2 = self.client.get(reverse("project-list"))
        assert res2.status_code in [200, 403, 404]
        self.client.credentials()

        # Rafraîchit le token
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
        """Vérifie qu'un token échoue avec des identifiants invalides."""
        token_url = "/o/token/"
        payload = {
            "grant_type": "password",
            "username": "existing",
            "password": "wrongpass",
        }

        res = self._post_form(token_url, payload, **self._basic_auth_header())
        assert res.status_code == 400
        assert "invalid_grant" in res.content.decode().lower()
