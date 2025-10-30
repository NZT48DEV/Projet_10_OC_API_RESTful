"""
Vues principales du module projects.
Gèrent la logique de création, lecture, mise à jour et suppression
pour les entités Project, Contributor, Issue et Comment.
Incluent des optimisations via cache, select_related et prefetch_related.
"""

import logging
import uuid
from collections import defaultdict

from django.core.cache import cache
from django.db import IntegrityError, transaction
from drf_spectacular.utils import OpenApiResponse, extend_schema
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
from projects.throttles import InviteThrottle
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import User
from utils.cache_tools import safe_delete_pattern

logger = logging.getLogger("projects.invites")


# ---------------------------------------------------------------------
# PROJETS
# ---------------------------------------------------------------------
class ProjectViewSet(viewsets.ModelViewSet):
    """Vue principale de gestion des projets."""

    permission_classes = [IsAuthenticated, IsAuthorAndContributor]

    def get_serializer_class(self):
        """Sélectionne le serializer selon l’action."""
        return (
            ProjectListSerializer
            if self.action == "list"
            else ProjectDetailSerializer
        )

    def get_queryset(self):
        """Récupère la liste des projets avec cache et préchargement."""
        user = self.request.user
        cache_key = f"user_projects_{user.id}"

        cached_projects = cache.get(cache_key)
        if cached_projects is not None:
            print(f"Cache utilisé pour {cache_key}")
            return cached_projects

        print(
            f"Aucun cache trouvé pour {cache_key}, reconstruction en cours..."
        )

        qs = (
            Project.objects.select_related("author_user")
            .prefetch_related("contributors__user")
            .distinct()
        )
        if not user.is_superuser:
            qs = qs.filter(contributors__user=user)

        cache.set(cache_key, qs, timeout=600)
        print(f"Cache créé pour {cache_key} (durée 600s)")

        return qs

    def list(self, request, *args, **kwargs):
        """Affiche les projets de l’utilisateur avec message personnalisé."""
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
        """Crée un projet et son auteur-contributeur associé."""
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
        """Crée un projet et renvoie un message clair."""
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

    @extend_schema(
        responses={
            200: {
                "type": "object",
                "example": {
                    "message": "Le projet '{title}' et ses données associées ont été supprimés.",
                    "status": "success",
                },
            }
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Supprime un projet et nettoie le cache associé."""
        instance = self.get_object()
        user = request.user
        title = instance.title

        self.perform_destroy(instance)

        safe_delete_pattern(f"user_projects_{user.id}")
        safe_delete_pattern(f"issues_user_{user.id}_project_*")

        return Response(
            {
                "message": (
                    f"Le projet '{title}' et ses données associées "
                    "ont été supprimés."
                ),
                "status": "success",
            },
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# CONTRIBUTEURS
# ---------------------------------------------------------------------
class ContributorViewSet(viewsets.ModelViewSet):
    """Vue de gestion des contributeurs (ajout via UUID sécurisé, suppression standard)."""

    permission_classes = [IsAuthenticated, IsAuthorAndContributor]
    pagination_class = ContributorProjectPagination
    throttle_classes = []  # définies dynamiquement par action

    def get_serializer_class(self):
        """Choisit un serializer selon l’action en cours."""
        return (
            ContributorListSerializer
            if self.action == "list"
            else ContributorDetailSerializer
        )

    def get_queryset(self):
        """Retourne la liste des contributeurs accessibles."""
        user = self.request.user
        qs = Contributor.objects.select_related("project", "user")
        if user.is_superuser:
            return qs
        return qs.filter(project__contributors__user=user).distinct()

    def list(self, request, *args, **kwargs):
        """Regroupe les contributeurs par projet."""
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

    # ------------------------------------------------------------------
    # AJOUT VIA BODY (UUID sécurisé)
    # ------------------------------------------------------------------
    @extend_schema(
        summary="Ajoute un contributeur via son UUID utilisateur (réponse uniforme)",
        description="Ajoute silencieusement un contributeur sans divulguer d'information sur l'existence du compte.",
        request={
            "application/json": {
                "example": {
                    "project": 1,
                    "user_uuid": "96085b35-cc7c-4cc8-b202-8ea5c5135bcd",
                }
            }
        },
        responses={
            200: OpenApiResponse(description="Réponse uniforme."),
            429: OpenApiResponse(description="Trop de tentatives."),
            403: OpenApiResponse(description="Accès refusé."),
        },
    )
    def create(self, request, *args, **kwargs):
        """Ajout sécurisé de contributeur via UUID avec throttle et réponse uniforme."""

        if not self._check_throttle(request):
            return Response(
                {"detail": "Trop de tentatives. Réessayez plus tard."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        project, user = self._validate_invite_params(request)
        if not project or not user:
            return self._uniform_response()

        self._add_contributor_silently(project, user)
        return self._uniform_response()

    # ------------------------------------------------------------------
    # Méthodes utilitaires privées
    # ------------------------------------------------------------------

    def _check_throttle(self, request):
        """Vérifie la limite de tentatives d’ajout."""
        throttle = InviteThrottle()
        return throttle.allow_request(request, self)

    def _log_invite_attempt(self, request, project_id, user_uuid):
        """Log les tentatives d’ajout de contributeur."""
        ip = request.META.get("REMOTE_ADDR") or request.META.get(
            "HTTP_X_FORWARDED_FOR"
        )
        logger.info(
            "invite_attempt",
            extra={
                "actor_id": request.user.id,
                "actor_username": request.user.username,
                "project_id": project_id,
                "target_uuid": user_uuid,
                "ip": ip,
            },
        )

    def _validate_invite_params(self, request):
        """Valide le projet et le UUID, et retourne (project, user) si tout est valide."""
        project_id = request.data.get("project")
        user_uuid = request.data.get("user_uuid")

        self._log_invite_attempt(request, project_id, user_uuid)

        # Vérifie que les deux paramètres sont fournis
        if not project_id or not user_uuid:
            return None, None

        # Vérifie le projet
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return None, None

        # Vérifie les droits d'accès
        if (
            project.author_user != request.user
            and not request.user.is_superuser
        ):
            return None, None

        # Vérifie le format UUID et l’existence du user
        try:
            uuid.UUID(str(user_uuid))
            user = User.objects.get(uuid=user_uuid)
        except (ValueError, AttributeError, TypeError, User.DoesNotExist):
            return None, None

        return project, user

    def _add_contributor_silently(self, project, user):
        """Ajoute le contributeur si nécessaire, sans erreur si doublon."""
        try:
            if not Contributor.objects.filter(
                user=user, project=project
            ).exists():
                with transaction.atomic():
                    Contributor.objects.create(
                        user=user,
                        project=project,
                        permission=(
                            "AUTHOR"
                            if project.author_user == user
                            else "CONTRIBUTOR"
                        ),
                        role=(
                            "Auteur et Contributeur du projet"
                            if project.author_user == user
                            else "Contributeur"
                        ),
                    )
                    safe_delete_pattern(f"user_projects_{user.id}")
                    safe_delete_pattern(f"issues_user_{user.id}_project_*")
        except IntegrityError:
            logger.exception(
                "invite_db_error",
                extra={"project": project.id, "user_uuid": user.uuid},
            )

    def _uniform_response(self):
        """Renvoie une réponse uniforme pour préserver la confidentialité."""
        return Response(
            {"detail": "Si l'utilisateur existe, il a été ajouté ou invité."},
            status=status.HTTP_200_OK,
        )

    # ------------------------------------------------------------------
    # SUPPRESSION STANDARD (par ID)
    # ------------------------------------------------------------------
    @extend_schema(
        summary="Supprime un contributeur par son ID",
        description="Supprime un contributeur du projet de façon classique.",
        responses={
            200: {
                "type": "object",
                "example": {
                    "message": "Le contributeur '{username}' a été retiré du projet.",
                    "status": "success",
                },
            },
            403: OpenApiResponse(
                description="Impossible de retirer l’auteur."
            ),
        },
    )
    def destroy(self, request, *args, **kwargs):
        """Supprime un contributeur par son ID (classique)."""
        instance = self.get_object()
        user = instance.user
        project_id = instance.project.id

        # Empêche la suppression de l’auteur du projet
        if instance.permission == "AUTHOR":
            return Response(
                {"detail": "Impossible de retirer l’auteur du projet."},
                status=status.HTTP_403_FORBIDDEN,
            )

        self.perform_destroy(instance)

        safe_delete_pattern(f"user_projects_{user.id}")
        safe_delete_pattern(f"issues_user_{user.id}_project_*")
        safe_delete_pattern(f"issues_project_{project_id}")

        return Response(
            {
                "message": f"Le contributeur '{user.username}' a été retiré du projet.",
                "status": "success",
            },
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# ISSUES
# ---------------------------------------------------------------------
class IssueViewSet(viewsets.ModelViewSet):
    """Vue principale pour la gestion des issues."""

    permission_classes = [
        IsAuthenticated,
        IsAuthorOrProjectContributorReadOnly,
    ]

    def get_serializer_class(self):
        """Retourne le serializer selon l’action."""
        return (
            IssueListSerializer
            if self.action == "list"
            else IssueDetailSerializer
        )

    def get_queryset(self):
        """Charge les issues avec cache et relations optimisées."""
        user = self.request.user
        project_id = self.request.query_params.get("project")
        cache_key = f"issues_user_{user.id}_project_{project_id or 'all'}"

        cached_issues = cache.get(cache_key)
        if cached_issues is not None:
            return cached_issues

        qs = Issue.objects.select_related(
            "project",
            "project__author_user",
            "author_user",
            "assignee_contributor",
            "assignee_contributor__user",
        ).distinct()

        if not user.is_superuser:
            qs = qs.filter(project__contributors__user=user)

        if project_id:
            qs = qs.filter(project_id=project_id)

        cache.set(cache_key, qs, timeout=600)
        return qs

    def list(self, request, *args, **kwargs):
        """Liste les issues accessibles à l’utilisateur."""
        user = request.user
        if not Project.objects.filter(contributors__user=user).exists():
            return Response(
                {"detail": "Accès refusé : aucun projet associé."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().list(request, *args, **kwargs)

    # ------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------
    def perform_create(self, serializer):
        """Crée une issue et valide les permissions associées."""
        user = self.request.user
        project = serializer.validated_data.get("project")
        assignee_contributor = serializer.validated_data.get(
            "assignee_contributor"
        )

        # Vérifie que l’auteur est contributeur du projet
        is_contrib = project.contributors.filter(user=user).exists()
        if not (is_contrib or project.author_user == user):
            raise PermissionDenied(
                "Accès refusé : vous devez être contributeur d’un projet pour créer une issue."
            )

        # Vérifie que l’assigné fait bien partie du projet
        if assignee_contributor and assignee_contributor.project != project:
            raise ValidationError(
                {
                    "detail": "Le contributeur assigné doit appartenir au même projet."
                }
            )

        issue = serializer.save(author_user=user)

        # Invalidation des caches liés
        safe_delete_pattern(f"issues_user_{user.id}_project_*")
        safe_delete_pattern(f"issues_project_{project.id}")

        return issue

    def create(self, request, *args, **kwargs):
        """Crée une issue avec message clair et lien d’assignation."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        issue = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        assignee = issue.assignee_contributor
        msg = f"Issue '{issue.title}' créée"
        if assignee and assignee.user:
            msg += f" et assignée à '{assignee.user.username}'"
        msg += "."

        data = {"message": msg}
        data.update(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    # ------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------
    def perform_update(self, serializer):
        """Met à jour une issue en vérifiant que seul l’auteur ou l’assigné peut modifier."""
        issue = self.get_object()
        user = self.request.user

        # Récupère le contributeur assigné (actualisé)
        assignee_contributor = issue.assignee_contributor

        # Vérifie que l'utilisateur est bien l'auteur ou l'assigné
        if not (
            issue.author_user == user
            or (assignee_contributor and assignee_contributor.user == user)
        ):
            raise PermissionDenied(
                "Seul l’auteur ou l’assigné peut modifier cette issue."
            )

        serializer.save()

        # Invalidation du cache après modification
        safe_delete_pattern(f"issues_user_{user.id}_project_*")
        safe_delete_pattern(f"issues_project_{issue.project.id}")

    # ------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------
    @extend_schema(
        responses={
            200: {
                "type": "object",
                "example": {
                    "message": "L’issue '{title}' a bien été supprimée.",
                    "status": "success",
                },
            }
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Supprime une issue et nettoie les caches associés."""
        instance = self.get_object()
        title = instance.title
        project_id = instance.project_id
        user_id = request.user.id

        self.perform_destroy(instance)

        # Invalidation du cache
        safe_delete_pattern(f"issues_user_{user_id}_project_*")
        safe_delete_pattern(f"issues_project_{project_id}")

        return Response(
            {
                "message": f"L’issue '{title}' a bien été supprimée.",
                "status": "success",
            },
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------
# COMMENTAIRES
# ---------------------------------------------------------------------
class CommentViewSet(viewsets.ModelViewSet):
    """Vue principale pour la gestion des commentaires."""

    permission_classes = [
        IsAuthenticated,
        IsAuthorOrProjectContributorReadOnly,
    ]

    def get_serializer_class(self):
        """Retourne le serializer selon l’action."""
        return (
            CommentListSerializer
            if self.action == "list"
            else CommentDetailSerializer
        )

    def get_queryset(self):
        """Charge les commentaires liés aux issues accessibles."""
        user = self.request.user
        qs = Comment.objects.select_related(
            "issue",
            "issue__project",
            "issue__assignee_contributor",
            "author_user",
        ).distinct()
        if user.is_superuser:
            return qs
        return qs.filter(issue__project__contributors__user=user)

    def list(self, request, *args, **kwargs):
        """Liste les commentaires selon les droits de l’utilisateur."""
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
        """Crée un commentaire après vérification des droits."""
        issue = serializer.validated_data.get("issue")
        project = issue.project
        user = self.request.user
        desc = serializer.validated_data.get("description")

        if not (
            project.contributors.filter(user=user).exists()
            or project.author_user == user
        ):
            raise PermissionDenied("Vous devez être contributeur du projet.")

        if Comment.objects.filter(
            issue=issue, author_user=user, description__iexact=desc
        ).exists():
            raise ValidationError(
                {"detail": "Un commentaire identique existe déjà."}
            )

        try:
            serializer.save(author_user=user)
        except IntegrityError:
            raise ValidationError(
                {"detail": "Un commentaire identique existe déjà."}
            )

    def create(self, request, *args, **kwargs):
        """Crée un commentaire et renvoie un message clair."""
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

    def perform_update(self, serializer):
        """Empêche la duplication lors de la mise à jour d’un commentaire."""
        try:
            serializer.save()
        except IntegrityError:
            raise ValidationError(
                {"detail": "Un commentaire identique existe déjà."}
            )

    @extend_schema(
        responses={
            200: {
                "type": "object",
                "example": {
                    "message": "Le commentaire n°{id} a bien été supprimé avec succès.",
                    "status": "success",
                },
            }
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Supprime un commentaire et renvoie un message de confirmation."""
        instance = self.get_object()
        comment_id = instance.id
        self.perform_destroy(instance)

        return Response(
            {
                "message": f"Le commentaire n°{comment_id} a bien été supprimé avec succès.",
                "status": "success",
            },
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
