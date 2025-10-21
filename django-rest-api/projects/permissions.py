from rest_framework import permissions


class IsContributor(permissions.BasePermission):
    """
    Permission générale :
    - Un utilisateur doit être contributeur du projet lié à la ressource
      pour pouvoir y accéder.
    - L’auteur du projet est considéré comme contributeur.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
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
    def has_permission(self, request, view):
        if request.method == "POST":
            return request.user and request.user.is_authenticated
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method in permissions.SAFE_METHODS:
            if hasattr(obj, "contributors"):
                return obj.contributors.filter(user=user).exists()
            if hasattr(obj, "project"):
                return obj.project.contributors.filter(user=user).exists()
            return False

        author_attr = getattr(obj, "author_user", None)

        if author_attr is None and hasattr(obj, "project"):
            return obj.project.author_user == user

        return author_attr == user


class IsAuthorOrProjectContributorReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if request.method in permissions.SAFE_METHODS:
            if hasattr(obj, "issue"):
                project = obj.issue.project
            elif hasattr(obj, "project"):
                project = obj.project
            else:
                return False

            return (
                project.contributors.filter(user=user).exists()
                or project.author_user == user
                or getattr(obj, "assignee_user", None) == user
            )

        # Écriture : réservée à l’auteur ou à l’utilisateur assigné
        if hasattr(obj, "assignee_user") and obj.assignee_user == user:
            return True

        return getattr(obj, "author_user", None) == user
