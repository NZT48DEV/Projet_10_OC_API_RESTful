from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée :
    - Tous les contributeurs peuvent lire une ressource (GET, HEAD, OPTIONS)
    - Seul l'auteur peut la modifier ou la supprimer (PUT, PATCH, DELETE)
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class IsContributor(permissions.BasePermission):
    """
    Permission :
    l'utilisateur doit être contributeur du projet lié à la ressource.
    """

    def has_permission(self, request, view):
        """
        Vérifie l'accès à la liste ou à la création d'une ressource.
        Exemple : /projects/ ou /issues/
        """
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Vérifie l'accès à une ressource spécifique (Project, Issue, Comment)
        """
        user = request.user

        # Si c'est un projet -> vérifier les contributeurs
        if hasattr(obj, "contributors"):
            return user in obj.contributors.all()

        # Si c'est une issue -> vérifier le projet lié
        if hasattr(obj, "project"):
            return user in obj.project.contributors.all()

        # Si c'est un commentaire -> vérifier via issue.project
        if hasattr(obj, "issue"):
            return user in obj.issue.project.contributors.all()

        return False


class IsAuthorAndContributor(permissions.BasePermission):
    """
    Autorise :
    - la lecture pour les contributeurs du projet
    - la modification/suppression seulement pour l’auteur
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Lecture : autorisée si le user est contributeur du projet
        if request.method in permissions.SAFE_METHODS:
            if hasattr(obj, "project"):
                return obj.project.contributors.filter(user=user).exists()
            if hasattr(obj, "issue"):
                return obj.issue.project.contributors.filter(
                    user=user
                ).exists()
            if hasattr(obj, "contributors"):  # Projet
                return obj.contributors.filter(user=user).exists()
            return False

        # Écriture : autorisée uniquement pour l’auteur
        author_attr = getattr(obj, "author_user", None)
        return author_attr == user
