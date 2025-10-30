"""
Configuration de l’interface d’administration Django pour le module projects.
Définit l’affichage, les filtres et les champs en lecture seule
pour les modèles Project, Contributor, Issue et Comment.
"""

from django.contrib import admin

from .models import Comment, Contributor, Issue, Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Configuration d’affichage du modèle Project dans l’admin Django."""

    list_display = ("id", "title", "type", "author_user", "created_time")
    search_fields = ("title", "description")
    list_filter = ("type",)
    ordering = ("-created_time",)
    readonly_fields = ("created_time",)


@admin.register(Contributor)
class ContributorAdmin(admin.ModelAdmin):
    """Configuration d’affichage du modèle Contributor."""

    list_display = ("id", "user", "project", "permission", "role")
    search_fields = ("user__username", "project__title")
    list_filter = ("permission",)
    ordering = ("id",)


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    """Configuration d’affichage du modèle Issue."""

    list_display = (
        "id",
        "title",
        "project",
        "author_user",
        "assignee_contributor",
        "priority",
        "status",
    )
    search_fields = ("title", "description")
    list_filter = ("priority", "status")
    ordering = ("-created_time",)
    readonly_fields = ("created_time",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Configuration d’affichage du modèle Comment."""

    list_display = ("id", "issue", "author_user", "created_time")
    search_fields = ("description",)
    ordering = ("-created_time",)
    readonly_fields = ("created_time",)
