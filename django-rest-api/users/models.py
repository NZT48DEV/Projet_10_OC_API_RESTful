from django.contrib.auth.models import AbstractUser
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


class User(AbstractUser):
    age = models.PositiveIntegerField(validators=[validate_age])
    can_be_contacted = models.BooleanField()
    can_data_be_shared = models.BooleanField()
    created_time = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # On force la validation complète avant la sauvegarde
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
