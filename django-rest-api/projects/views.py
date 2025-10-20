from projects.models import Comment, Contributor, Issue, Project
from projects.permissions import (
    IsAuthorAndContributor,
    IsAuthorOrProjectContributorReadOnly,
)
from projects.serializers import (
    CommentSerializer,
    ContributorSerializer,
    IssueSerializer,
    ProjectSerializer,
)
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated


class ProjectViewSet(viewsets.ModelViewSet):
    """
    Gestion des projets :
    - Lecture : autorisée aux contributeurs et à l’auteur.
    - Création : ouverte à tout utilisateur authentifié.
    - Modification/Suppression : réservées à l’auteur du projet.
    """

    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsAuthorAndContributor]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Project.objects.all()
        return Project.objects.filter(contributors__user=user).distinct()

    def perform_create(self, serializer):
        project = serializer.save(author_user=self.request.user)
        Contributor.objects.create(
            user=self.request.user,
            project=project,
            permission="AUTHOR",
            role="Auteur et Contributeur du projet",
        )


class ContributorViewSet(viewsets.ModelViewSet):
    """
    Gestion des contributeurs :
    - Lecture : accessible aux contributeurs et à l’auteur du projet.
    - Création / suppression : réservées à l’auteur du projet.
    """

    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated, IsAuthorAndContributor]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Contributor.objects.all()
        return Contributor.objects.filter(project__contributors__user=user)

    def perform_create(self, serializer):
        """Seul l’auteur du projet peut ajouter un contributeur."""
        project = serializer.validated_data.get("project")
        if project.author_user != self.request.user:
            raise PermissionDenied(
                "Seul l’auteur du projet peut ajouter un contributeur."
            )
        serializer.save()

    def perform_destroy(self, instance):
        """Seul l’auteur du projet peut retirer un contributeur."""
        if instance.project.author_user != self.request.user:
            raise PermissionDenied(
                "Seul l’auteur du projet peut retirer un contributeur."
            )
        instance.delete()


class IssueViewSet(viewsets.ModelViewSet):
    """
    Gestion des issues (tickets) :
    - Lecture : autorisée aux contributeurs du projet.
    - Création : autorisée uniquement aux contributeurs du projet.
    - Modification/Suppression : réservées à l’auteur de l’issue.
    """

    serializer_class = IssueSerializer
    permission_classes = [
        IsAuthenticated,
        IsAuthorOrProjectContributorReadOnly,
    ]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Issue.objects.all()
        return Issue.objects.filter(
            project__contributors__user=user
        ).distinct()

    def perform_create(self, serializer):
        user = self.request.user
        project = serializer.validated_data.get("project")

        is_contributor = project.contributors.filter(user=user).exists()
        if not (is_contributor or project.author_user == user):
            raise PermissionDenied(
                "Vous devez être contributeur du projet pour créer une issue."
            )

        serializer.save(author_user=user)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Gestion des commentaires :
    - Lecture : autorisée aux contributeurs du projet.
    - Création : autorisée pour les contributeurs du projet.
    - Modification/Suppression : réservée à l’auteur du commentaire.
    """

    serializer_class = CommentSerializer
    permission_classes = [
        IsAuthenticated,
        IsAuthorOrProjectContributorReadOnly,
    ]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Comment.objects.all()
        return Comment.objects.filter(
            issue__project__contributors__user=user
        ).distinct()

    def perform_create(self, serializer):
        issue = serializer.validated_data.get("issue")
        project = issue.project
        user = self.request.user

        # Vérifie que l’utilisateur est contributeur ou auteur du projet
        is_contributor = project.contributors.filter(user=user).exists()
        if not (is_contributor or project.author_user == user):
            raise PermissionDenied(
                "Vous devez être contributeur du projet pour commenter."
            )

        serializer.save(author_user=user)
