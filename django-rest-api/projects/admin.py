from django.contrib import admin

from .models import Comment, Contributor, Issue, Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "type", "author_user", "created_time")
    search_fields = ("title", "description")
    list_filter = ("type",)
    ordering = ("-created_time",)
    readonly_fields = ("created_time",)


@admin.register(Contributor)
class ContributorAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "project", "permission", "role")
    search_fields = ("user__username", "project__title")
    list_filter = ("permission",)
    ordering = ("id",)


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "project",
        "author_user",
        "assignee_user",
        "priority",
        "status",
    )
    search_fields = ("title", "description")
    list_filter = ("priority", "status")
    ordering = ("-created_time",)
    readonly_fields = ("created_time",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "issue", "author_user", "created_time")
    search_fields = ("description",)
    ordering = ("-created_time",)
    readonly_fields = ("created_time",)
