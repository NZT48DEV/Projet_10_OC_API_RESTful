"""
Définition des permissions personnalisées du module projects.
Ces classes contrôlent l'accès aux projets, issues et commentaires
en fonction du rôle et du lien entre l'utilisateur et la ressource.
"""

from rest_framework import permissions


class IsContributor(permissions.BasePermission):
    """
    Vérifie que l'utilisateur est contributeur du projet associé.
    L'auteur du projet est considéré comme contributeur.
    """

    def has_permission(self, request, view):
        """Autorise uniquement les utilisateurs authentifiés."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Vérifie l’appartenance du user au projet lié à l’objet."""
        user = request.user

        if hasattr(obj, "contributors"):
            return obj.contributors.filter(user=user).exists()

        if hasattr(obj, "project"):
            project = obj.project
            return (
                project.contributors.filter(user=user).exists()
                or project.author_user == user
            )

        if hasattr(obj, "issue"):
            project = obj.issue.project
            return (
                project.contributors.filter(user=user).exists()
                or project.author_user == user
            )

        return False


class IsAuthorAndContributor(permissions.BasePermission):
    """
    Autorise :
    - la lecture aux contributeurs du projet,
    - l'écriture uniquement à l'auteur de la ressource.
    """

    def has_permission(self, request, view):
        """Autorise les requêtes authentifiées selon la méthode HTTP."""
        if request.method == "POST":
            return request.user and request.user.is_authenticated
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        """Vérifie les droits selon la méthode et le lien à l'objet."""
        user = request.user

        # Lecture seule : doit être contributeur
        if request.method in permissions.SAFE_METHODS:
            if hasattr(obj, "contributors"):
                return obj.contributors.filter(user=user).exists()
            if hasattr(obj, "project"):
                return obj.project.contributors.filter(user=user).exists()
            return False

        # Écriture : réservée à l’auteur
        author_attr = getattr(obj, "author_user", None)
        if author_attr is None and hasattr(obj, "project"):
            return obj.project.author_user == user
        return author_attr == user


class IsAuthorOrProjectContributorReadOnly(permissions.BasePermission):
    """
    Autorise :
    - la lecture aux contributeurs et à l’auteur du projet,
    - la modification uniquement à l’auteur ou à l’utilisateur assigné.
    """

    def has_object_permission(self, request, view, obj):
        """Contrôle les droits d'accès selon le contexte d’objet."""
        user = request.user

        # Lecture : auteur, contributeur ou assigné
        if request.method in permissions.SAFE_METHODS:
            if hasattr(obj, "issue"):
                project = obj.issue.project
            elif hasattr(obj, "project"):
                project = obj.project
            else:
                return False

            # L’utilisateur peut lire s’il est contributeur, auteur ou assigné
            return (
                project.contributors.filter(user=user).exists()
                or project.author_user == user
                or (
                    hasattr(obj, "assignee_contributor")
                    and obj.assignee_contributor
                    and obj.assignee_contributor.user == user
                )
            )

        # Écriture : réservée à l’auteur ou à l’utilisateur assigné
        if (
            hasattr(obj, "assignee_contributor")
            and obj.assignee_contributor
            and obj.assignee_contributor.user == user
        ):
            return True

        return getattr(obj, "author_user", None) == user
