from projects.models import Comment, Contributor, Issue, Project
from rest_framework import serializers


class ContributorSerializer(serializers.ModelSerializer):
    is_author = serializers.SerializerMethodField()

    class Meta:
        model = Contributor
        fields = ["id", "user", "project", "permission", "role", "is_author"]

    def get_is_author(self, obj):
        return obj.permission == "AUTHOR"


class ProjectSerializer(serializers.ModelSerializer):
    author_user_id = serializers.ReadOnlyField(source="author_user.id")
    author_username = serializers.ReadOnlyField(source="author_user.username")
    contributors = ContributorSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "type",
            "author_user_id",
            "author_username",
            "created_time",
            "contributors",
        ]


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
