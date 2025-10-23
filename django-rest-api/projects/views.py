from collections import defaultdict

from django.core.cache import cache
from django.db import IntegrityError, transaction
from projects.models import Comment, Contributor, Issue, Project
from projects.pagination import ContributorProjectPagination
from projects.permissions import (
    IsAuthorAndContributor,
    IsAuthorOrProjectContributorReadOnly,
)
from projects.serializers import (
    CommentDetailSerializer,
    CommentListSerializer,
    ContributorDetailSerializer,
    ContributorListSerializer,
    IssueDetailSerializer,
    IssueListSerializer,
    ProjectDetailSerializer,
    ProjectListSerializer,
)
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from utils.cache_tools import safe_delete_pattern


# -----------------------------
#  PROJETS
# -----------------------------
class ProjectViewSet(viewsets.ModelViewSet):
    """Optimisation via cache, select_related et prefetch_related."""

    permission_classes = [IsAuthenticated, IsAuthorAndContributor]

    def get_serializer_class(self):
        return (
            ProjectListSerializer
            if self.action == "list"
            else ProjectDetailSerializer
        )

    def get_queryset(self):
        user = self.request.user
        cache_key = f"user_projects_{user.id}"

        cached_projects = cache.get(cache_key)
        if cached_projects is not None:
            return cached_projects

        qs = (
            Project.objects.select_related("author_user")
            .prefetch_related("contributors__user")
            .distinct()
        )
        if not user.is_superuser:
            qs = qs.filter(contributors__user=user)

        cache.set(cache_key, qs, timeout=600)
        return qs

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
                {"detail": "Un projet avec ce titre existe déjà."}
            )

        try:
            project = serializer.save(author_user=user)
            Contributor.objects.create(
                user=user,
                project=project,
                permission="AUTHOR",
                role="Auteur et Contributeur du projet",
            )
            cache.delete(f"user_projects_{user.id}")
        except IntegrityError:
            raise ValidationError(
                {"detail": "Ce projet existe déjà dans la base."}
            )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        project = serializer.instance
        return Response(
            {
                "message": f"Projet '{project.title}' créé avec succès.",
                "project": serializer.data,
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        self.perform_destroy(instance)
        cache.delete(f"user_projects_{user.id}")
        return Response(
            status=status.HTTP_204_NO_CONTENT, content_type="application/json"
        )


# -----------------------------
#  CONTRIBUTEURS
# -----------------------------
class ContributorViewSet(viewsets.ModelViewSet):
    """Optimisation via select_related sur user et project."""

    permission_classes = [IsAuthenticated, IsAuthorAndContributor]
    pagination_class = ContributorProjectPagination

    def get_serializer_class(self):
        return (
            ContributorListSerializer
            if self.action == "list"
            else ContributorDetailSerializer
        )

    def get_queryset(self):
        user = self.request.user
        qs = Contributor.objects.select_related("project", "user")
        if user.is_superuser:
            return qs
        return qs.filter(project__contributors__user=user).distinct()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response(
                {"detail": "Accès refusé : aucun projet associé."},
                status=status.HTTP_403_FORBIDDEN,
            )
        grouped = defaultdict(list)
        for contributor in queryset:
            grouped[contributor.project.id].append(contributor)
        projects = [
            {
                "project_id": pid,
                "project_title": c[0].project.title,
                "project_type": c[0].project.type,
                "contributors_count": len(c),
                "contributors": ContributorListSerializer(
                    c, many=True, context={"request": request}
                ).data,
            }
            for pid, c in grouped.items()
        ]
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(projects, request)
        if not page:
            return Response([], status=status.HTTP_200_OK)
        return paginator.get_paginated_response(page)

    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                serializer.save()
        except IntegrityError:
            raise ValidationError(
                {"detail": "Cet utilisateur est déjà contributeur."}
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            status=status.HTTP_204_NO_CONTENT, content_type="application/json"
        )


# -----------------------------
#  ISSUES
# -----------------------------
class IssueViewSet(viewsets.ModelViewSet):
    """Optimisation via cache fin et select_related sur relations uniques."""

    permission_classes = [
        IsAuthenticated,
        IsAuthorOrProjectContributorReadOnly,
    ]

    def get_serializer_class(self):
        return (
            IssueListSerializer
            if self.action == "list"
            else IssueDetailSerializer
        )

    def get_queryset(self):
        user = self.request.user
        project_id = self.request.query_params.get("project")
        cache_key = f"issues_user_{user.id}_project_{project_id or 'all'}"

        cached_issues = cache.get(cache_key)
        if cached_issues is not None:
            return cached_issues

        qs = Issue.objects.select_related(
            "project", "project__author_user", "author_user", "assignee_user"
        ).distinct()

        if not user.is_superuser:
            qs = qs.filter(project__contributors__user=user)

        if project_id:
            qs = qs.filter(project_id=project_id)

        cache.set(cache_key, qs, timeout=600)
        return qs

    def list(self, request, *args, **kwargs):
        user = request.user
        if not Project.objects.filter(contributors__user=user).exists():
            return Response(
                {"detail": "Accès refusé : aucun projet associé."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = self.request.user
        project = serializer.validated_data.get("project")

        is_contrib = project.contributors.filter(user=user).exists()
        if not (is_contrib or project.author_user == user):
            raise PermissionDenied(
                "Accès refusé : vous devez être contributeur "
                "d’un projet pour créer une issue."
            )

        assignee = serializer.validated_data.get("assignee_user")
        if (
            assignee
            and not project.contributors.filter(user=assignee).exists()
        ):
            raise ValidationError(
                {"detail": "L'utilisateur assigné doit être contributeur."}
            )

        serializer.save(author_user=user)

        # ✅ Invalidation du cache des issues (compatible tous backends)
        safe_delete_pattern(f"issues_user_{user.id}_project_*")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        issue = serializer.instance
        assignee = issue.assignee_user
        msg = f"Issue '{issue.title}' créée"
        if assignee:
            msg += f" et assignée à '{assignee.username}'."
        else:
            msg += "."
        data = {"message": msg}
        data.update(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


# -----------------------------
#  COMMENTAIRES
# -----------------------------
class CommentViewSet(viewsets.ModelViewSet):
    """Optimisation via select_related sur issue et auteur."""

    permission_classes = [
        IsAuthenticated,
        IsAuthorOrProjectContributorReadOnly,
    ]

    def get_serializer_class(self):
        return (
            CommentListSerializer
            if self.action == "list"
            else CommentDetailSerializer
        )

    def get_queryset(self):
        user = self.request.user
        qs = Comment.objects.select_related(
            "issue", "issue__project", "issue__assignee_user", "author_user"
        ).distinct()
        if user.is_superuser:
            return qs
        return qs.filter(issue__project__contributors__user=user)

    def list(self, request, *args, **kwargs):
        user = request.user
        if not Project.objects.filter(contributors__user=user).exists():
            return Response(
                {"detail": "Accès refusé : aucun projet associé."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if (
            not Issue.objects.filter(project__contributors__user=user).exists()
            and not Issue.objects.filter(project__author_user=user).exists()
        ):
            return Response(
                {"detail": "Aucune issue trouvée."},
                status=status.HTTP_200_OK,
            )
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        issue = serializer.validated_data.get("issue")
        project = issue.project
        user = self.request.user
        desc = serializer.validated_data.get("description")
        is_contrib = project.contributors.filter(user=user).exists()
        if not (is_contrib or project.author_user == user):
            raise PermissionDenied("Vous devez être contributeur.")
        if Comment.objects.filter(
            issue=issue, author_user=user, description__iexact=desc
        ).exists():
            raise ValidationError(
                {"detail": "Un commentaire identique existe déjà."}
            )
        serializer.save(author_user=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        comment = serializer.instance
        issue = comment.issue
        msg = f"Commentaire ajouté à l’issue '{issue.title}'."
        issue_url = f"http://127.0.0.1:8000/api/issues/{issue.id}/"
        data = {"message": msg, "issue_url": issue_url}
        data.update(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            status=status.HTTP_204_NO_CONTENT, content_type="application/json"
        )
