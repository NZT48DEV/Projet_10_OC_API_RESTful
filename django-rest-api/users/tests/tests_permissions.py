import pytest
from rest_framework.test import APIClient
from users.models import User


@pytest.mark.django_db
class TestUserPermissions:
    """Tests essentiels sur les permissions RGPD des utilisateurs."""

    def setup_method(self):
        """Création des utilisateurs avant chaque test (DB disponible)."""
        self.client = APIClient()

        self.alice = User.objects.create_user(
            username="alice",
            password="pass1234",
            can_be_contacted=True,
            can_data_be_shared=True,
            age=25,
        )
        self.bob = User.objects.create_user(
            username="bob",
            password="pass1234",
            can_be_contacted=False,
            can_data_be_shared=False,
            age=30,
        )

    # --- LECTURE / LISTE ---
    def test_authenticated_user_sees_only_self(self):
        """Un utilisateur authentifié ne voit que son propre profil."""
        self.client.force_authenticate(user=self.alice)
        res = self.client.get("/api/users/", HTTP_ACCEPT="application/json")

        assert res.status_code == 200
        data = res.json()
        results = data.get("results", data)
        assert len(results) == 1
        assert results[0]["username"] == "alice"

    # --- MODIFICATION ---
    def test_user_can_update_self_but_not_others(self):
        """Un utilisateur peut modifier ses infos, pas celles d’autrui."""
        self.client.force_authenticate(user=self.alice)

        # ✅ Mise à jour de soi-même
        res_self = self.client.patch(
            f"/api/users/{self.alice.id}/",
            {"can_data_be_shared": False},
            format="json",
        )
        assert res_self.status_code in [200, 202]
        self.alice.refresh_from_db()
        assert self.alice.can_data_be_shared is False

        # 🚫 Tentative de mise à jour d’un autre utilisateur
        res_other = self.client.patch(
            f"/api/users/{self.bob.id}/",
            {"can_be_contacted": True},
            format="json",
        )
        assert res_other.status_code in [403, 404]
        self.bob.refresh_from_db()
        assert self.bob.can_be_contacted is False

    # --- SUPPRESSION ---
    def test_user_can_delete_self_only(self):
        """Un utilisateur peut supprimer uniquement son compte."""
        self.client.force_authenticate(user=self.bob)
        res = self.client.delete(f"/api/users/{self.bob.id}/")
        assert res.status_code in [200, 204]
        assert not User.objects.filter(id=self.bob.id).exists()

    # --- CREATION ---
    def test_authenticated_user_cannot_create_new_account(self):
        """Un utilisateur déjà connecté ne peut pas créer un autre compte."""
        self.client.force_authenticate(user=self.alice)
        res = self.client.post(
            "/api/users/",
            {
                "username": "new_user",
                "password": "pass1234",
                "age": 25,
                "can_be_contacted": True,
                "can_data_be_shared": True,
            },
            format="json",
        )
        assert res.status_code in [403, 405]
