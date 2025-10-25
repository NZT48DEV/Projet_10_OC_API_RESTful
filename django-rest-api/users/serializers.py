"""
Définition des serializers du module users.
Gère la sérialisation des informations publiques et complètes
du modèle utilisateur, avec validation et sécurisation du mot de passe.
"""

from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User


# ---------------------------------------------------------------------
# UTILISATEURS – LISTE
# ---------------------------------------------------------------------
class UserListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour afficher les informations publiques."""

    class Meta:
        model = User
        fields = ["id", "username", "age", "created_time"]
        read_only_fields = ["id", "created_time"]


# ---------------------------------------------------------------------
# UTILISATEURS – DÉTAIL / CRÉATION / ÉDITION
# ---------------------------------------------------------------------
class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour la gestion complète du profil."""

    username = serializers.CharField(
        min_length=3,
        max_length=30,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Ce nom d'utilisateur existe déjà.",
            ),
            RegexValidator(
                regex=r"^[a-zA-Z0-9_]+$",
                message=(
                    "Le nom d’utilisateur ne doit contenir que des lettres, "
                    "chiffres ou underscores (_)."
                ),
            ),
        ],
    )

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "age",
            "can_be_contacted",
            "can_data_be_shared",
            "created_time",
        ]
        read_only_fields = ["id", "created_time"]

    def create(self, validated_data):
        """Crée un utilisateur avec mot de passe hashé."""
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user
