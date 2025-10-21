from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models


def validate_age(value):
    if value < 15:
        raise ValidationError(
            (
                "Âge invalide : %(value)s ans. "
                "L'utilisateur doit avoir au moins 15 ans pour s'inscrire."
            ),
            params={"value": value},
        )


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError("Le champ 'username' est obligatoire.")
        if "age" not in extra_fields:
            raise ValueError("Le champ 'age' est obligatoire.")
        if "can_be_contacted" not in extra_fields:
            raise ValueError("Le champ 'can_be_contacted' est obligatoire.")
        if "can_data_be_shared" not in extra_fields:
            raise ValueError("Le champ 'can_data_be_shared' est obligatoire.")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, username, email=None, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        extra_fields.setdefault("age", 30)
        extra_fields.setdefault("can_be_contacted", False)
        extra_fields.setdefault("can_data_be_shared", False)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    age = models.PositiveIntegerField(validators=[validate_age])
    can_be_contacted = models.BooleanField()
    can_data_be_shared = models.BooleanField()
    created_time = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
