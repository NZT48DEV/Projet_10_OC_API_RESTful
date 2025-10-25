"""
Tests unitaires du modèle personnalisé User.
Vérifie la création, la validation et les contraintes de champs.
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

User = get_user_model()


class UserModelTest(TestCase):
    """Tests essentiels du modèle User."""

    @classmethod
    def setUpTestData(cls):
        """Prépare des données valides pour l’ensemble des tests."""
        cls.valid_data = {
            "username": "alice",
            "password": "pass123",
            "age": 25,
            "can_be_contacted": True,
            "can_data_be_shared": False,
        }

    def test_create_user_valid(self):
        """Vérifie la création d’un utilisateur valide."""
        user = User.objects.create_user(**self.valid_data)
        self.assertEqual(user.username, "alice")
        self.assertEqual(str(user), "alice")
        self.assertTrue(user.can_be_contacted)
        self.assertFalse(user.can_data_be_shared)

    def test_user_age_validation(self):
        """Âge < 15 doit lever une ValidationError."""
        invalid_data = self.valid_data.copy()
        invalid_data["age"] = 10
        user = User(**invalid_data)
        with self.assertRaises(ValidationError) as context:
            user.full_clean()
        self.assertIn("Âge invalide", str(context.exception))

    def test_boolean_fields_required(self):
        """Les champs booléens doivent être renseignés."""
        user = User(username="charlie", password="pass123", age=20)
        with self.assertRaises(ValidationError):
            user.full_clean()
