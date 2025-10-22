from django.contrib.auth import get_user_model
from django.db.models import Q
from projects.models import Comment, Contributor, Issue, Project
from rest_framework import serializers

User = get_user_model()


class ContributorSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_superuser=False)
    )
    username = serializers.ReadOnlyField(source="user.username")
    project_url = serializers.HyperlinkedRelatedField(
        source="project",
        view_name="project-detail",
        read_only=True,
    )
    delete_contributeur_url = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()

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

    def validate(self, data):
        user = data.get("user")
        project = data.get("project")

        if not user:
            raise serializers.ValidationError(
                {"detail": "L’utilisateur est requis."}
            )

        if not project:
            raise serializers.ValidationError(
                {"detail": "Le projet est requis."}
            )

        if user == project.author_user:
            raise serializers.ValidationError(
                {
                    "detail": (
                        "L’auteur du projet est déjà contributeur par défaut."
                    )
                }
            )

        if user.is_superuser:
            raise serializers.ValidationError(
                {
                    "detail": (
                        "Les superutilisateurs ne peuvent pas être "
                        "contributeurs."
                    )
                }
            )

        return data

    def create(self, validated_data):
        user = validated_data["user"]
        project = validated_data["project"]

        if Contributor.objects.filter(user=user, project=project).exists():
            raise serializers.ValidationError(
                {"detail": "Cet utilisateur est déjà contributeur du projet."}
            )

        validated_data["permission"] = "CONTRIBUTOR"
        validated_data["role"] = "Contributeur du projet"
        return super().create(validated_data)


class ProjectSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="project-detail",
        lookup_field="pk",
        read_only=True,
    )
    author_user_id = serializers.ReadOnlyField(source="author_user.id")
    author_username = serializers.ReadOnlyField(source="author_user.username")
    contributors = ContributorSerializer(many=True, read_only=True)

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")

        if request and not request.user.is_superuser:
            self.fields["contributors"].queryset = Contributor.objects.filter(
                project__contributors__user=request.user
            )


class IssueSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source="author_user.username")
    assignee_username = serializers.ReadOnlyField(
        source="assignee_user.username"
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
            "assignee_user",
            "assignee_username",
            "project",
            "project_title",
            "created_time",
        ]
        read_only_fields = ["author_user", "created_time"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")

        if request and not request.user.is_superuser:
            user = request.user

            self.fields["project"].queryset = Project.objects.filter(
                contributors__user=user
            ).distinct()

            self.fields["assignee_user"].queryset = User.objects.filter(
                projects_contributed__project__contributors__user=user
            ).distinct()

            instance = getattr(self, "instance", None)
            if instance and getattr(instance, "assignee_user", None) == user:
                for field_name in self.fields.keys():
                    if field_name != "status":
                        self.fields[field_name].read_only = True


class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source="author_user.username")
    issue_title = serializers.ReadOnlyField(source="issue.title")

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
            "created_time",
        ]
        read_only_fields = ["author_user", "created_time", "uuid"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")

        if request and not request.user.is_superuser:
            user = request.user
            from projects.models import Issue  # éviter import circulaire

            self.fields["issue"].queryset = Issue.objects.filter(
                Q(project__contributors__user=user)
                | Q(project__author_user=user)
            ).distinct()
