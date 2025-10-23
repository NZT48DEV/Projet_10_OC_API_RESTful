from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

User = get_user_model()


class UserModelTest(TestCase):
    """Tests essentiels du modèle User optimisés."""

    @classmethod
    def setUpTestData(cls):
        """Créé une seule fois pour tous les tests (gain de temps)."""
        cls.valid_data = dict(
            username="alice",
            password="pass123",
            age=25,
            can_be_contacted=True,
            can_data_be_shared=False,
        )

    def test_create_user_valid(self):
        """Création d’un utilisateur valide."""
        user = User.objects.create_user(**self.valid_data)
        self.assertEqual(user.username, "alice")
        self.assertEqual(str(user), "alice")
        self.assertTrue(user.can_be_contacted)
        self.assertFalse(user.can_data_be_shared)

    def test_user_age_validation(self):
        """Âge inférieur à 15 → ValidationError."""
        invalid_data = self.valid_data.copy()
        invalid_data["age"] = 10
        user = User(**invalid_data)
        with self.assertRaises(ValidationError) as context:
            user.full_clean()
        self.assertIn("Âge invalide", str(context.exception))

    def test_boolean_fields_required(self):
        """Les champs booléens sont obligatoires."""
        user = User(
            username="charlie",
            password="pass123",
            age=20,
        )
        with self.assertRaises(ValidationError):
            user.full_clean()
