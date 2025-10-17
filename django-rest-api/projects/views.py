from projects.models import Comment, Contributor, Issue, Project
from projects.permissions import IsAuthorAndContributor
from projects.serializers import (
    CommentSerializer,
    ContributorSerializer,
    IssueSerializer,
    ProjectSerializer,
)
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsAuthorAndContributor]

    def get_queryset(self):
        """Renvoie tous les projets, la permission gère le filtrage."""
        return Project.objects.all()

    def perform_create(self, serializer):
        project = serializer.save(author_user=self.request.user)
        Contributor.objects.create(
            user=self.request.user,
            project=project,
            permission="AUTHOR",
            role="Auteur du projet",
        )


class ContributorViewSet(viewsets.ModelViewSet):
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated, IsAuthorAndContributor]

    def get_queryset(self):
        return Contributor.objects.filter(
            project__contributors__user=self.request.user
        )


class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated, IsAuthorAndContributor]

    def get_queryset(self):
        return Issue.objects.all()

    def perform_create(self, serializer):
        serializer.save(author_user=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsAuthorAndContributor]

    def get_queryset(self):
        return Comment.objects.all()

    def perform_create(self, serializer):
        serializer.save(author_user=self.request.user)
