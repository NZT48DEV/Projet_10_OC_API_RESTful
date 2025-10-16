from rest_framework import serializers
from projects.models import Project, Contributor

class ContributorSerializer(serializers.ModelSerializer):
    # En lecture seule, pour éviter de modifier l'utilisateur depuis une requête POST.
    user_id = serializers.ReadOnlyField(source='user.id')
    username = serializers.ReadOnlyField(source='user.username')
    

    class Meta:
        model = Contributor
        fields = ['id', 'user_id', 'username', 'project', 'permission', 'role']

class ProjectSerializer(serializers.ModelSerializer):
    author_user_id = serializers.ReadOnlyField(source='author_user.id')
    author_username = serializers.ReadOnlyField(source='author_user.username')
    contributors = ContributorSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'id',
            'title',
            'description',
            'type',
            'author_user_id',
            'author_username',
            'created_time',
            'contributors',
        ]