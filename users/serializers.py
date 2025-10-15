from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'age',
            'can_be_contacted', 'can_data_be_shared', 'created_time'
        ]
        read_only_fields = ['id', 'created_time']
        extra_kwargs = {
            'password': {'write_only': True},
        }


    def create(self, validated_data):
        """Création sécurisée avec hash du mot de passe"""
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user