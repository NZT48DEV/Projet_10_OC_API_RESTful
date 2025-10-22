from rest_framework import serializers

from .models import User


# --- Serializer léger (liste) ---
class UserListSerializer(serializers.ModelSerializer):
    """Affiche uniquement les infos publiques d’un utilisateur."""

    class Meta:
        model = User
        fields = ["id", "username", "age", "created_time"]
        read_only_fields = ["id", "created_time"]


# --- Serializer détaillé (création / édition / détail) ---
class UserDetailSerializer(serializers.ModelSerializer):
    """Affiche et gère les infos complètes d’un utilisateur."""

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
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        """Création sécurisée avec hash du mot de passe."""
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user
