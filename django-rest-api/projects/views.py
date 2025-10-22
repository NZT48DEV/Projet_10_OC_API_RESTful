from django.db import IntegrityError
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
from rest_framework import serializers, status, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsAuthorAndContributor]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Project.objects.all()
        return Project.objects.filter(contributors__user=user).distinct()

    def list(self, request, *args, **kwargs):
        user = request.user

        if not Project.objects.filter(contributors__user=user).exists():
            return Response(
                {
                    "detail": (
                        "Vous n'avez encore aucun projet, "
                        "mais vous pouvez en créer un ci-dessous."
                    )
                },
                status=status.HTTP_200_OK,
            )

        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        title = serializer.validated_data.get("title")
        user = self.request.user

        if Project.objects.filter(
            title__iexact=title, author_user=user
        ).exists():
            raise ValidationError(
                {
                    "detail": (
                        "Un projet avec ce titre existe déjà pour cet auteur."
                    )
                }
            )

        try:
            project = serializer.save(author_user=user)
            Contributor.objects.create(
                user=user,
                project=project,
                permission="AUTHOR",
                role="Auteur et Contributeur du projet",
            )
        except IntegrityError:
            raise ValidationError(
                {"detail": "Ce projet existe déjà dans la base de données."}
            )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        project = serializer.instance
        return Response(
            {
                "message": (
                    f"✅ Le projet '{project.title}' "
                    "a été créé avec succès !"
                ),
                "project": serializer.data,
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class ContributorViewSet(viewsets.ModelViewSet):
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated, IsAuthorAndContributor]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Contributor.objects.all()
        return Contributor.objects.filter(
            project__contributors__user=user
        ).distinct()

    def list(self, request, *args, **kwargs):
        user = request.user
        if not Contributor.objects.filter(
            project__contributors__user=user
        ).exists():
            raise PermissionDenied(
                "Accès refusé : vous devez être contributeur d’un projet "
                "pour voir cette ressource."
            )
        return super().list(request, *args, **kwargs)

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        serializer = serializer_class(*args, **kwargs)

        if not isinstance(serializer, serializers.ListSerializer):
            if hasattr(serializer.Meta, "validators"):
                serializer.Meta.validators = []
        return serializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=False)

        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        project = serializer.validated_data.get("project")
        user_to_add = serializer.validated_data.get("user")

        if project.author_user != request.user:
            raise PermissionDenied(
                "Seul l’auteur du projet peut ajouter un contributeur."
            )

        if Contributor.objects.filter(
            project=project, user=user_to_add
        ).exists():
            return Response(
                {
                    "detail": (
                        f"L'utilisateur '{user_to_add.username}' "
                        f"est déjà contributeur du projet '{project.title}'."
                    ),
                    "project_url": (
                        f"http://127.0.0.1:8000/api/projects/{project.id}/"
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            {
                "message": (
                    f"L'utilisateur '{user_to_add.username}' "
                    "a bien été ajouté comme contributeur "
                    f"au projet '{project.title}'."
                ),
                "contributor": serializer.data,
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def perform_create(self, serializer):
        project = serializer.validated_data.get("project")
        user = serializer.validated_data.get("user")

        if project.author_user != self.request.user:
            raise PermissionDenied(
                "Seul l’auteur du projet peut ajouter un contributeur."
            )

        if Contributor.objects.filter(project=project, user=user).exists():
            raise ValidationError(
                {"detail": "Cet utilisateur est déjà contributeur du projet."}
            )

        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.project.author_user != request.user:
            raise PermissionDenied(
                "Seul l’auteur du projet peut retirer un contributeur."
            )
        if instance.user == instance.project.author_user:
            raise ValidationError(
                {"detail": "L’auteur du projet ne peut pas être retiré."}
            )

        username = instance.user.username
        project_name = instance.project.title

        self.perform_destroy(instance)
        return Response(
            {
                "message": (
                    f"L'utilisateur '{username}' "
                    f"a bien été retiré du projet '{project_name}'."
                ),
                "status": "success",
            },
            status=status.HTTP_200_OK,
        )


class IssueViewSet(viewsets.ModelViewSet):
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

    def list(self, request, *args, **kwargs):
        user = request.user

        if not Project.objects.filter(contributors__user=user).exists():
            raise PermissionDenied(
                "Accès refusé : vous devez être contributeur d’un projet "
                "pour voir cette ressource."
            )

        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = self.request.user
        project = serializer.validated_data.get("project")

        is_contributor = project.contributors.filter(user=user).exists()
        if not (is_contributor or project.author_user == user):
            raise PermissionDenied(
                "Vous devez être contributeur du projet pour créer une issue."
            )

        assignee_user = serializer.validated_data.get("assignee_user")
        if (
            assignee_user
            and not project.contributors.filter(user=assignee_user).exists()
        ):
            raise ValidationError(
                {
                    "detail": (
                        "L'utilisateur assigné doit être "
                        "contributeur du projet."
                    )
                }
            )

        serializer.save(author_user=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        issue = serializer.instance
        assignee_user = issue.assignee_user

        message = f"✅ Issue '{issue.title}' créée avec succès" + (
            f" et assignée à '{assignee_user.username}' !"
            if assignee_user
            else " !"
        )

        data = {"message": message}
        data.update(serializer.data)

        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        kwargs.pop("partial", False)
        instance = self.get_object()
        user = request.user
        project = instance.project

        if (
            not project.contributors.filter(user=user).exists()
            and user != project.author_user
        ):
            raise PermissionDenied(
                "Vous devez être contributeur du projet "
                "pour modifier cette issue."
            )

        if instance.author_user == user:
            return super().update(request, *args, **kwargs)

        if instance.assignee_user == user:
            if set(request.data.keys()) == {"status"}:
                instance.status = request.data["status"]
                instance.save()
                return Response(
                    self.get_serializer(instance).data,
                    status=status.HTTP_200_OK,
                )
            raise ValidationError(
                {
                    "detail": (
                        "Vous ne pouvez modifier que le champ 'status' "
                        "de cette issue."
                    )
                }
            )

        raise PermissionDenied(
            "Seul l’auteur ou l’utilisateur assigné "
            "peut modifier cette issue."
        )


class CommentViewSet(viewsets.ModelViewSet):
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

    def list(self, request, *args, **kwargs):
        user = request.user

        if not Project.objects.filter(contributors__user=user).exists():
            raise PermissionDenied(
                "Accès refusé : vous devez être contributeur d’un projet "
                "pour voir cette ressource."
            )

        if (
            not Issue.objects.filter(project__contributors__user=user).exists()
            and not Issue.objects.filter(project__author_user=user).exists()
        ):
            return Response(
                {
                    "detail": (
                        "Aucune issue n’a encore été créée pour vos projets."
                    )
                },
                status=status.HTTP_200_OK,
            )

        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        issue = serializer.validated_data.get("issue")
        project = issue.project
        user = self.request.user
        description = serializer.validated_data.get("description")

        is_contributor = project.contributors.filter(user=user).exists()
        if not (is_contributor or project.author_user == user):
            raise PermissionDenied(
                "Vous devez être contributeur du projet pour commenter."
            )

        if Comment.objects.filter(
            issue=issue,
            author_user=user,
            description__iexact=description,
        ).exists():
            raise ValidationError(
                {
                    "detail": (
                        "Un commentaire identique existe déjà sur cette issue."
                    )
                }
            )

        serializer.save(author_user=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        comment = serializer.instance
        issue = comment.issue

        message = (
            f"💬 Commentaire ajouté avec succès à l’issue '{issue.title}' !"
        )
        issue_url = f"http://127.0.0.1:8000/api/issues/{issue.id}/"

        data = {
            "message": message,
            "issue_url": issue_url,
        }
        data.update(serializer.data)

        return Response(data, status=status.HTTP_201_CREATED, headers=headers)
