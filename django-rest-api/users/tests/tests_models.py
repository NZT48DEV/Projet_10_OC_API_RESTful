from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

User = get_user_model()


class UserModelTest(TestCase):
    def test_user_creation_valid(self):
        user = User.objects.create_user(
            username="alice",
            password="pass123",
            age=25,
            can_be_contacted=True,
            can_data_be_shared=False,
        )
        self.assertEqual(user.username, "alice")
        self.assertEqual(user.age, 25)
        self.assertTrue(user.can_be_contacted)
        self.assertFalse(user.can_data_be_shared)
        self.assertIsNotNone(user.created_time)
        self.assertEqual(str(user), "alice")

    def test_user_creation_invalid_age(self):
        user = User(
            username="bob",
            password="pass123",
            age=10,
            can_be_contacted=True,
            can_data_be_shared=False,
        )
        with self.assertRaises(ValidationError) as context:
            user.full_clean()
        self.assertIn("Âge invalide", str(context.exception))

    def test_user_missing_booleans(self):
        user = User(
            username="charlie",
            password="pass123",
            age=20,
        )
        with self.assertRaises(ValidationError):
            user.full_clean()
