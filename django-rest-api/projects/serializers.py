"""
Définition des serializers du module projects.
Gère la sérialisation des entités Project, Contributor, Issue et Comment
pour la communication entre l’API et le client.
"""

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from projects.models import Comment, Contributor, Issue, Project
from rest_framework import serializers

User = get_user_model()

# ---------------------------------------------------------------------
# CONTRIBUTEURS
# ---------------------------------------------------------------------


class ContributorListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des contributeurs."""

    username = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Contributor
        fields = ["id", "username", "role"]


class ContributorDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour la gestion des contributeurs (ajout via UUID)."""

    user_uuid = serializers.UUIDField(write_only=True, required=True)
    username = serializers.ReadOnlyField(source="user.username")
    project_url = serializers.HyperlinkedRelatedField(
        source="project", view_name="project-detail", read_only=True
    )
    is_author = serializers.SerializerMethodField()
    created_time = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Contributor
        fields = [
            "id",
            "user_uuid",
            "username",
            "project",
            "project_url",
            "permission",
            "role",
            "is_author",
            "created_time",
        ]
        read_only_fields = ["permission", "role"]
        validators = []

    def validate_user_uuid(self, value):
        """Valide l’existence du user à partir de l’UUID fourni."""
        from users.models import User  # import local pour éviter les boucles

        try:
            user = User.objects.get(uuid=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Utilisateur introuvable.")
        self._validated_user = user
        return value

    def create(self, validated_data):
        """
        Crée un contributeur avec l’utilisateur identifié par UUID.
        Remplace le champ 'user_uuid' par l’instance utilisateur.
        """
        validated_data["user"] = self._validated_user
        validated_data.pop("user_uuid", None)
        return super().create(validated_data)

    def get_is_author(self, obj):
        """Renvoie True si le contributeur est l’auteur du projet."""
        return obj.permission == "AUTHOR"

    def __init__(self, *args, **kwargs):
        """Filtre les choix projet selon le contexte de l’utilisateur."""
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and not request.user.is_superuser:
            user = request.user
            self.fields["project"].queryset = Project.objects.filter(
                author_user=user
            )


# ---------------------------------------------------------------------
# PROJETS
# ---------------------------------------------------------------------


class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des projets."""

    author_username = serializers.ReadOnlyField(source="author_user.username")

    class Meta:
        model = Project
        fields = ["id", "title", "type", "author_username"]


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour les projets."""

    url = serializers.HyperlinkedIdentityField(
        view_name="project-detail", lookup_field="pk", read_only=True
    )
    author_user_id = serializers.ReadOnlyField(source="author_user.id")
    author_username = serializers.ReadOnlyField(source="author_user.username")
    contributors = ContributorListSerializer(many=True, read_only=True)
    created_time = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "url",
            "title",
            "description",
            "type",
            "author_user_id",
            "author_username",
            "created_time",
            "contributors",
        ]


# ---------------------------------------------------------------------
# ISSUES
# ---------------------------------------------------------------------


class IssueListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des issues."""

    author_username = serializers.ReadOnlyField(source="author_user.username")
    assignee_contributor_id = serializers.ReadOnlyField(
        source="assignee_contributor.id"
    )
    assignee_contributor_username = serializers.ReadOnlyField(
        source="assignee_contributor.user.username"
    )
    project_title = serializers.ReadOnlyField(source="project.title")

    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "status",
            "tag",
            "priority",
            "author_username",
            "assignee_contributor_id",
            "assignee_contributor_username",
            "project_title",
            "created_time",
        ]


class IssueDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour afficher ou modifier une issue."""

    author_username = serializers.ReadOnlyField(source="author_user.username")
    assignee_contributor = serializers.PrimaryKeyRelatedField(
        queryset=Contributor.objects.all(),
        required=False,
        allow_null=True,
    )
    assignee_contributor_username = serializers.ReadOnlyField(
        source="assignee_contributor.user.username"
    )
    project_title = serializers.ReadOnlyField(source="project.title")

    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "description",
            "tag",
            "priority",
            "status",
            "author_user",
            "author_username",
            "assignee_contributor",
            "assignee_contributor_username",
            "project",
            "project_title",
            "created_time",
        ]
        read_only_fields = ["author_user", "created_time"]

    def __init__(self, *args, **kwargs):
        """Restreint les contributeurs assignables à ceux du projet concerné."""
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user:
            self.fields["assignee_contributor"].queryset = (
                self.get_filtered_contributors(request)
            )

    def get_filtered_contributors(self, request):
        """Retourne uniquement les contributeurs appartenant au projet."""
        project = None

        # Si on modifie une issue existante
        if self.instance and getattr(self.instance, "project", None):
            project = self.instance.project
        else:
            # Si on crée une nouvelle issue
            data = getattr(self, "initial_data", {})
            project_id = data.get("project")
            if project_id:
                project = Project.objects.filter(id=project_id).first()

        # On restreint aux contributeurs du projet + auteur du projet
        if project:
            return Contributor.objects.filter(project=project)
        return Contributor.objects.none()


# ---------------------------------------------------------------------
# COMMENTAIRES
# ---------------------------------------------------------------------


class CommentListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des commentaires."""

    author_username = serializers.ReadOnlyField(source="author_user.username")
    issue_url = serializers.HyperlinkedRelatedField(
        source="issue", view_name="issue-detail", read_only=True
    )

    class Meta:
        model = Comment
        fields = ["id", "author_username", "description", "issue_url"]


class CommentDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour les commentaires."""

    author_username = serializers.ReadOnlyField(source="author_user.username")
    issue_title = serializers.ReadOnlyField(source="issue.title")
    created_time = serializers.DateTimeField(read_only=True)
    issue_url = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "uuid",
            "description",
            "author_user",
            "author_username",
            "issue",
            "issue_title",
            "issue_url",
            "created_time",
        ]
        read_only_fields = ["author_user", "created_time", "uuid"]

    def __init__(self, *args, **kwargs):
        """Filtre les issues accessibles à l’utilisateur courant."""
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user and not request.user.is_superuser:
            self.fields["issue"].queryset = self.get_filtered_issues(
                request.user
            )

    def get_filtered_issues(self, user):
        """Renvoie les issues accessibles à l’utilisateur."""
        return Issue.objects.filter(
            models.Q(project__contributors__user=user)
            | models.Q(project__author_user=user)
        ).distinct()

    def get_issue_url(self, obj):
        """Construit l’URL complète d’une issue associée."""
        request = self.context.get("request")
        if request and obj.issue:
            url = reverse("issue-detail", args=[obj.issue.id])
            return request.build_absolute_uri(url)
        return None
