import pytest
from rest_framework.test import APIClient
from users.models import User


@pytest.mark.django_db
class TestUserPermissions:
    """Vérifie les permissions RGPD sur les utilisateurs."""

    def setup_method(self):
        self.client = APIClient()

        # Création de deux utilisateurs
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

    # ----------------------------------
    # 🔹 DELETE /api/users/{id}/
    # ----------------------------------

    def test_user_can_delete_self(self):
        """Un utilisateur peut supprimer uniquement son propre compte."""
        self.client.force_authenticate(user=self.alice)
        response = self.client.delete(f"/api/users/{self.alice.id}/")
        assert response.status_code == 204
        assert not User.objects.filter(id=self.alice.id).exists()

    def test_user_cannot_delete_other_user(self):
        """Un utilisateur ne peut pas supprimer le compte d'un autre."""
        self.client.force_authenticate(user=self.alice)
        response = self.client.delete(f"/api/users/{self.bob.id}/")
        assert response.status_code == 403
        assert User.objects.filter(id=self.bob.id).exists()

    def test_anonymous_cannot_delete_any_user(self):
        """Un utilisateur non authentifié ne peut rien supprimer."""
        response = self.client.delete(f"/api/users/{self.alice.id}/")
        assert response.status_code == 401

    # ----------------------------------
    # 🔹 PATCH /api/users/{id}/
    # ----------------------------------

    def test_user_can_update_self(self):
        """Un utilisateur peut modifier ses propres informations."""
        self.client.force_authenticate(user=self.alice)
        response = self.client.patch(
            f"/api/users/{self.alice.id}/",
            {"can_data_be_shared": False},
            format="json",
        )
        assert response.status_code == 200
        self.alice.refresh_from_db()
        assert self.alice.can_data_be_shared is False

    def test_user_cannot_update_other_user(self):
        """Un utilisateur ne peut pas modifier les données d'un autre."""
        self.client.force_authenticate(user=self.alice)
        response = self.client.patch(
            f"/api/users/{self.bob.id}/",
            {"can_be_contacted": True},
            format="json",
        )
        assert response.status_code == 403
        self.bob.refresh_from_db()
        assert self.bob.can_be_contacted is False
