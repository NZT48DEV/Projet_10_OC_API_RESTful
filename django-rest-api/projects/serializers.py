from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from projects.models import Comment, Contributor, Issue, Project
from rest_framework import serializers

User = get_user_model()


# -----------------------------
#  SERIALIZERS CONTRIBUTEUR
# -----------------------------


class ContributorListSerializer(serializers.ModelSerializer):
    """Serializer léger pour lister les contributeurs."""

    username = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Contributor
        fields = ["id", "username", "role"]


class ContributorDetailSerializer(serializers.ModelSerializer):
    """Serializer complet pour les contributeurs."""

    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_superuser=False)
    )
    username = serializers.ReadOnlyField(source="user.username")
    project_url = serializers.HyperlinkedRelatedField(
        source="project", view_name="project-detail", read_only=True
    )
    delete_contributeur_url = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()
    created_time = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Contributor
        fields = [
            "id",
            "user",
            "username",
            "project",
            "project_url",
            "permission",
            "role",
            "is_author",
            "delete_contributeur_url",
            "created_time",
        ]
        read_only_fields = ["permission", "role"]
        validators = []

    def get_is_author(self, obj):
        return obj.permission == "AUTHOR"

    def get_delete_contributeur_url(self, obj):
        if obj.permission == "AUTHOR":
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(f"/api/contributors/{obj.id}/")
        return f"/api/contributors/{obj.id}/"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and not request.user.is_superuser:
            user = request.user
            self.fields["project"].queryset = Project.objects.filter(
                author_user=user
            )
            self.fields["user"].queryset = User.objects.filter(
                is_superuser=False
            ).exclude(id=user.id)


# -----------------------------
#  SERIALIZERS PROJET
# -----------------------------


class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer léger pour les projets."""

    author_username = serializers.ReadOnlyField(source="author_user.username")

    class Meta:
        model = Project
        fields = ["id", "title", "type", "author_username"]


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour un projet."""

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


# -----------------------------
#  SERIALIZERS ISSUE
# -----------------------------


class IssueListSerializer(serializers.ModelSerializer):
    """Serializer léger pour les issues."""

    author_username = serializers.ReadOnlyField(source="author_user.username")

    class Meta:
        model = Issue
        fields = ["id", "title", "status", "author_username"]


class IssueDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour une issue."""

    author_username = serializers.ReadOnlyField(source="author_user.username")
    assignee_user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
    )
    assignee_username = serializers.ReadOnlyField(
        source="assignee_user.username"
    )
    project_title = serializers.ReadOnlyField(source="project.title")
    created_time = serializers.DateTimeField(read_only=True)

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
            "assignee_user",
            "assignee_username",
            "project",
            "project_title",
            "created_time",
        ]
        read_only_fields = ["author_user", "created_time"]

    def __init__(self, *args, **kwargs):
        """Restreint les utilisateurs assignables aux contributeurs du projet."""
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user:
            self.fields["assignee_user"].queryset = self.get_filtered_users(
                request
            )

    def get_filtered_users(self, request):
        """Renvoie la liste des utilisateurs assignables."""
        project = None

        if self.instance and getattr(self.instance, "project", None):
            project = self.instance.project
        else:
            data = getattr(self, "initial_data", {})
            project_id = data.get("project")
            if project_id:
                project = Project.objects.filter(id=project_id).first()

        if project:
            return User.objects.filter(
                models.Q(
                    id__in=project.contributors.values_list("user", flat=True)
                )
                | models.Q(id=project.author_user_id)
            ).distinct()

        return User.objects.filter(id=request.user.id)


# -----------------------------
#  SERIALIZERS COMMENTAIRE
# -----------------------------


class CommentListSerializer(serializers.ModelSerializer):
    """Serializer léger pour les commentaires."""

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
        """Filtre les issues selon les droits du contributeur."""
        super().__init__(*args, **kwargs)
        request = self.context.get("request")

        if request and request.user and not request.user.is_superuser:
            user = request.user
            self.fields["issue"].queryset = self.get_filtered_issues(user)

    def get_filtered_issues(self, user):
        """Renvoie les issues accessibles à l’utilisateur."""
        from projects.models import Issue

        return Issue.objects.filter(
            models.Q(project__contributors__user=user)
            | models.Q(project__author_user=user)
        ).distinct()

    def get_issue_url(self, obj):
        request = self.context.get("request")
        if request and obj.issue:
            url = reverse("issue-detail", args=[obj.issue.id])
            return request.build_absolute_uri(url)
        return None
